---
name: java-coding-style
description: UITC Java 小組後端編碼規範。當你要為與 UITC（com.uitc.*）合作對象撰寫、審查或重構 Java 後端程式（Controller/Service/Dao/Entity/DTO、Spring Boot、JPA、安全、稽核 log）時使用，確保新專案（Java 25 + Spring Boot 4）對齊命名、分層與技術慣例。功能模組沿用 ifrs16web 代號（AM/AP/CM/MM/PM + 四位數）僅命名 Controller。
metadata:
  author: IFRS16 team
  version: "2.0"
  targetStack: "Java 25 (LTS) + Spring Boot 4.0.6"
  basedOn: "ifrs16web 重構 + demo2 登入 API 實作驗證（2026-05）"
---

# UITC Java 小組後端編碼規範

本文件供 **ifrs16web 重構**（VB.NET WebForms → Java）及後續新專案對齊技術與命名慣例。
架構以 **Java 25 為主**，並以已驗證的 `demo2` 登入 API 實作為基準。

主要技術基準：

- **Java 25（LTS）**
- **Spring Boot 4.0.6**（Spring Framework 7 基礎）、`jakarta.*` 命名空間
- **Maven**（非 Gradle）
- **Lombok 1.18.64**
- **JUnit 6.1.0**（Jupiter）

當你為此小組寫後端程式時，**預設遵循本文件**。

---

## 0. 快速決策摘要（先讀這段）

| 主題 | 採用方式 |
|------|----------|
| 語言 / 框架 | Java 25 + Spring Boot 4.0.6 + Maven，`jakarta.*` |
| 分層 | `controller.api` → `service` → `dao` → `entity`，**`@Transactional` 放 Service 層**（無 `trx` 層） |
| 注入 | **constructor injection**（`@RequiredArgsConstructor` + `private final`；需 `@Value` 時用顯式建構子） |
| 資料存取 | Spring Data JPA + Hibernate，DAO 介面命名 **`*Dao extends JpaRepository`** |
| 資料庫 | **MSSQL**；對接既有資料表，欄位名**原樣對映**（見 §7） |
| API 回應 | 直接回 DTO 或 `ResponseEntity` + **RESTful 動詞**；錯誤交給全域 `@RestControllerAdvice` |
| 例外 | 自訂例外繼承 **`RuntimeException`** |
| DTO | **record 優先**，class 次之；語意命名 + 靜態 `parse()` |
| 功能模組代號 | 沿用 **ifrs16web 代號（AM/AP/CM/MM/PM + 四位數，如 `AM1000`）僅命名 Controller**；DTO / 稽核字串**不**帶代號（見 §1） |
| 安全 | Spring Security 6（`SecurityFilterChain` bean）+ **OAuth2 Resource Server（JWT，無狀態）** |
| 稽核 | 業務操作以 AOP 寫入 DB 稽核表 |
| 日誌 | **Logback**（`logback-spring.xml`）+ SLF4J；**不用** Log4j |
| 測試 | **JUnit 6.1.0 + Mockito**，**主寫 Service / Util 單元測試**；切片測試輔助（見 §11） |
| 縮排 | **Tab**（非空格） |

---

## 1. 功能模組代號（沿用 ifrs16web）

ifrs16web 既有的模組代號是**單純的功能識別碼**（經詢問確認），用 **兩碼字母 + 四位數字**，如 `AM1000`、`CM5000`、`AP2000`、`MM1000`、`PM2000`（字母為模組大類，如 AM/AP/CM/MM/PM；數字為子功能）。

重構成 Java 時的規則：

- **只用於 Controller 類別命名**，讓 REST 端點對應得回原 WebForms 畫面，方便對照。
  - 例：`AM1000.aspx` → `AM1000Controller`、`CM5000.aspx` → `CM5000Controller`。
- **DTO 不帶代號** — 用領域語意命名（見 §4）。
- **稽核動作字串不帶代號** — 用中文語意描述（見 §9）。
- **API URL 不綁代號** — 用 RESTful 資源路徑（見 §6）。
- 不對應任何 ifrs16web 模組的跨功能端點（如登入 `index`、共用查詢）以**語意命名** Controller（如 `AuthController`）。

> 即：代號只是「這支 Controller 對應哪個舊畫面」的標籤，不滲入 DTO、URL、稽核或 package。

---

## 2. 後端套件分層

### 2.1 標準 package 結構

根套件：`com.uitc.<projectname>`

```
com.uitc.<projectname>
├── <Project>Application.java     # @SpringBootApplication 啟動類
├── annotation/                   # 自訂 Annotation（如 @LogAction）
├── aspect/                       # AOP 切面（稽核 log）
├── config/                       # Security、JWT、OpenAPI 等設定
├── controller/
│   └── api/                      # @RestController：REST JSON API
├── advice/                       # 全域 @RestControllerAdvice
├── dao/                          # Spring Data JPA Repository 介面（命名 *Dao）
│   └── procedure/                # ← SP 入口（原 DLL 的 Exec_*）
│       ├── AmortizationProcedureDao.java    # 由 dll 反編譯來的程式重新製作
│       ├── VersionProcedureDao.java         # 註: dll 內幾乎都是 sql，操作核心業務資料表
│       └── ...
├── dto/                          # 請求 / 回應 DTO（record）
├── entity/                       # JPA Entity（對應既有 DB 表）
├── enums/                        # 列舉
├── exception/                    # 自訂例外（繼承 RuntimeException）
├── service/                      # 業務邏輯 + 交易邊界（@Transactional）
├── util/                         # 無狀態工具類
└── validator/                    # Bean Validation 自訂 Validator
```

> 約定：用 `entity`（不用 `model`）、`util`（單數）、切面放頂層 `aspect`、**無 `trx` 層**（交易直接放 Service）。

### 2.2 請求處理流程

```
Client
  │  Bearer JWT
  ▼
Security Filter（OAuth2 Resource Server 驗 JWT）
  ▼
Controller（@Valid 參數驗證、@PreAuthorize 角色檢查、委派 Service）
  │  @LogAction → AOP 攔截寫稽核
  ▼
Service（業務邏輯、@Transactional 交易邊界）
  │
  └── Dao（JpaRepository → DB）
```

預設為**單體應用**：單一 `pom.xml`、內嵌 Tomcat。若日後需呼叫外部服務，用 Boot 4 的 **`RestClient`**（不用舊的 `RestTemplate`）。

---

## 3. 類別職責約定

| 類型 | 後綴 | 註解 | 職責 |
|------|------|------|------|
| Controller | `*Controller`（含 ifrs16 代號或語意名） | `@RestController` | `@Valid` 驗證、`@PreAuthorize` 授權、委派 Service；**薄**，不放業務邏輯，**不直接注入 Dao** |
| Service | `*Service` | `@Service` | 業務流程、DTO↔Entity 轉換、**`@Transactional` 交易邊界**（查詢用 `readOnly = true`） |
| Dao | `*Dao` | `extends JpaRepository` | 介面 + 衍生查詢方法；複雜查詢用 `@Query` |
| Entity | （名詞，對應表名） | `@Entity` | JPA 實體，對應既有 DB 表 |
| DTO | `*Req` / `*Resp` / `*Dto` | `record` 優先 | API 契約，不含業務邏輯，靜態 `parse()` 轉換 |
| Validator | `*Validator` | — | Bean Validation 自訂規則 |
| Util | `*Util` | — | 無狀態工具方法 |

**交易策略**：`@Transactional` 放 **Service 層**；唯讀查詢標 `@Transactional(readOnly = true)`。不另設 `trx` 層。

---

## 4. 命名慣例

| 類型 | 慣例 | 範例 |
|------|------|------|
| Java 類別 | UpperCamelCase + 後綴表角色 | `AuthService`, `SUserDao`, `LoginReq` |
| Controller | ifrs16 代號 或 語意名 + `Controller` | `AM1000Controller`, `AuthController` |
| Java 方法／變數 | lowerCamelCase | `findByDeleteFlag`, `companyId` |
| DB Table / 欄位 | **對映既有 DB 實際名稱**（原樣，不轉換） | `@Table(name = "S_User")`, `@Column(name = "CompanyId")` |
| API Path | RESTful 資源路徑（不含模組代號） | `POST /api/auth/login`, `GET /api/auth/companies` |
| 密碼相關 | 縮寫 `Pd` / `pd`（避免拼出 password） | `UpdatePdReq`, `PdEncoderUtil` |
| DTO | 領域語意 + `Req` / `Resp` / `Dto`（**不帶模組代號**） | `LoginReq`, `LoginResp`, `CompanyResp`, `ErrorResp` |
| Enum 常數 | UPPER_SNAKE_CASE（可帶中文 description） | `DB("資料庫驗證")` |
| 設定 key | 小寫 + 點分隔 | `app.jwt.secret`, `app.jwt.expiration-seconds` |
| Maven artifactId | kebab-case | `ifrs16-web` |
| groupId / package | 全小寫，`com.uitc[.xxx]` | `com.uitc.demo2` |

規則重點：

- **Java 程式碼一律不用 snake_case**。DB 欄位**以既有資料庫實際命名為準**（ifrs16 為 PascalCase，如 `CompanyId`、`S_User`），用 `@Table`/`@Column` 原樣標註，**不要**自己改成大寫底線（見 §7 的 naming strategy）。
- **DAO 介面一律叫 `*Dao`**（`extends JpaRepository`），不要用 `*Repository`。
- 密碼一律以 `Pd` / `pd` 縮寫。

---

## 5. 程式碼格式與語言慣例

### 5.1 格式

- **縮排：Tab**（非空格）。
- 中文 Javadoc：方法用 `/** ... */`；Entity 欄位可用 `/*- ... */` 描述意義。
- 不要殘留 `System.out.println`、`printStackTrace()` 或註解掉的死碼。

### 5.2 依賴注入

- **constructor injection**：搭配 Lombok `@RequiredArgsConstructor` + `private final`。
- 需要 `@Value` 注入設定值的類別，改寫**顯式建構子**（仍是 constructor injection）。
- 不要用欄位注入（`@Autowired` on field）。

```java
@Service
@RequiredArgsConstructor
public class CompanyService {
	private final SCompanyDao sCompanyDao;
}

// 需要 @Value 時用顯式建構子
@Service
public class AuthService {
	private final SUserDao sUserDao;
	private final JwtEncoder jwtEncoder;
	private final long expirationSeconds;

	public AuthService(SUserDao sUserDao, JwtEncoder jwtEncoder,
			@Value("${app.jwt.expiration-seconds}") long expirationSeconds) {
		this.sUserDao = sUserDao;
		this.jwtEncoder = jwtEncoder;
		this.expirationSeconds = expirationSeconds;
	}
}
```

### 5.3 Lombok 與 record

- **DTO 優先用 `record`**（不可變、簡潔）；需要可變/框架要求 setter 時才用 class + Lombok `@Data`。
- Entity：用 Lombok `@Getter` / `@Setter`（避免 `@Data` 在 JPA 實體上的 `equals/hashCode` 陷阱）。
- Service / Util / Aspect：`@Slf4j` 取得 logger。
- DTO 轉換用 **靜態 factory `parse()` / `of()`**：

```java
public record LoginResp(String token, String userName, String roleId, String departmentId) {
	public static LoginResp parse(SUser user, String token) {
		return new LoginResp(token, user.getUserName(), user.getRoleId(), user.getDepartmentId());
	}
}
```

### 5.4 善用 Java 25 特性

- `record` 作 DTO；`sealed` 限制例外/狀態階層；`switch` pattern matching 處理狀態機。
- text block 寫多行 `@Query` JPQL。
- 型別明顯時用 `var`。
- 背景任務優先用 **Virtual Threads**（`spring.threads.virtual.enabled=true`）。

---

## 6. API 回應與例外處理

### 6.1 回應格式

- Controller **直接回傳 DTO** 或 `ResponseEntity<DTO>`，**不**包統一 Response Wrapper。
- **RESTful 動詞**：查詢 `GET`、建立 `POST`、更新 `PUT/PATCH`、刪除 `DELETE`。

```java
@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {
	private final AuthService authService;
	private final CompanyService companyService;

	@PostMapping("/login")
	public LoginResp login(@Valid @RequestBody LoginReq req) {
		return authService.login(req);
	}

	@GetMapping("/companies")
	public List<CompanyResp> companies() {
		return companyService.listActive();
	}
}
```

### 6.2 例外（全域處理 + RuntimeException）

- 自訂例外**繼承 `RuntimeException`**，放 `exception/`。
- 統一以 **`@RestControllerAdvice`**（放 `advice/`）轉成 HTTP 狀態 + 結構化 `ErrorResp`。
- 不在 Controller / Service 內 catch 後吞掉或 `printStackTrace`。

```java
@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {

	@ExceptionHandler(MethodArgumentNotValidException.class)
	public ResponseEntity<ErrorResp> handleValidation(MethodArgumentNotValidException e) {
		String msg = e.getBindingResult().getFieldErrors().stream()
				.findFirst().map(FieldError::getDefaultMessage).orElse("參數錯誤");
		return ResponseEntity.badRequest().body(ErrorResp.of(HttpStatus.BAD_REQUEST.value(), msg));
	}

	@ExceptionHandler(AuthenticationFailedException.class)
	public ResponseEntity<ErrorResp> handleAuthFailed(AuthenticationFailedException e) {
		log.warn("login failed: {}", e.getMessage());
		return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
				.body(ErrorResp.of(HttpStatus.UNAUTHORIZED.value(), e.getMessage()));
	}
}
```

驗證沿用「取第一個 FieldError 訊息」的慣例。

### 6.3 驗證

- 用 **Bean Validation（`jakarta.validation`）** + 自訂 Annotation（放 `validator/`）。
- Controller 參數用 `@Valid @RequestBody`；訊息可用中文。

---

## 7. 資料存取與資料庫

| 項目 | 規範 |
|------|------|
| DB | **MSSQL**（`com.microsoft.sqlserver:mssql-jdbc`） |
| ORM | Spring Data JPA + Hibernate（**非** MyBatis、非 pure JDBC） |
| DAO | `interface XxxDao extends JpaRepository<Entity, ID>`，衍生查詢方法 |
| 命名空間 | `jakarta.persistence.*` |
| 表/欄命名 | **對映既有 DB 實際名稱**，`@Table` / `@Column` 原樣標註 |
| 複合主鍵 | `@IdClass`（如 `S_User` 的 CompanyId + UserId） |
| Schema | 對接既有 DB 用 `spring.jpa.hibernate.ddl-auto=none`（不動結構） |

**關鍵設定（對接既有非 snake_case DB 必設）**：

ifrs16 的既有資料表是 **PascalCase**（`S_User`、`CompanyId`、`PasswordCheckFlag`…）。Spring Boot 預設的 `CamelCaseToUnderscoresNamingStrategy` 會把**明確指定的** `@Column("CompanyId")` 也轉成 `company_id`，導致實機報「無效的資料行名稱」。必須停用轉換：

```properties
spring.jpa.hibernate.naming.physical-strategy=org.hibernate.boot.model.naming.PhysicalNamingStrategyStandardImpl
spring.jpa.hibernate.ddl-auto=none
# dialect 由 Hibernate 依連線自動偵測，不需顯式指定（顯式指定會出 HHH90000025 warning）
```

> 注意：用 H2 `create-drop` 的切片測試會依 entity 自動建表，**會掩蓋欄位名不符**。測試與正式須採相同 naming strategy；對既有 DB 對映建議另以可連線環境或 Testcontainers 驗證。

```java
@Entity
@Table(name = "S_User")
@IdClass(SUserId.class)
@Getter
@Setter
public class SUser {
	@Id @Column(name = "CompanyId") private String companyId;
	@Id @Column(name = "UserId") private String userId;
	@Column(name = "PasswordCheckFlag") private String passwordCheckFlag;
	// ...
}
```

---

## 8. 安全架構

- **Spring Security 6**：用 `SecurityFilterChain` bean + lambda DSL，**不用**已棄用的 `WebSecurityConfigurerAdapter`。
- **JWT 用 Spring 內建 OAuth2 Resource Server**（`spring-boot-starter-security-oauth2-resource-server`）+ **Nimbus**（`NimbusJwtEncoder` / `NimbusJwtDecoder`）簽發與驗章，**不需 jjwt**。對稱金鑰用 HMAC（HS256）。
- 無狀態：`SessionCreationPolicy.STATELESS`、停用 CSRF。
- 方法級授權：`@EnableMethodSecurity` + `@PreAuthorize`。角色來源為既有 `S_Role`（RoleId）。
- 敏感設定（金鑰、密碼）以**環境變數**注入（`${JWT_SECRET:...}` 佔位），不寫死於檔案；必要時可加 Jasypt（`ENC(...)`）。

```java
@Configuration
@EnableMethodSecurity
public class SecurityConfig {

	@Bean
	SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
		http
			.csrf(AbstractHttpConfigurer::disable)
			.sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
			.authorizeHttpRequests(auth -> auth
				.requestMatchers(HttpMethod.POST, "/api/auth/login").permitAll()
				.requestMatchers(HttpMethod.GET, "/api/auth/companies").permitAll()
				.requestMatchers("/swagger-ui/**", "/v3/api-docs/**").permitAll()
				.anyRequest().authenticated())
			.oauth2ResourceServer(oauth -> oauth.jwt(Customizer.withDefaults()));
		return http.build();
	}
}
```

JWT 簽發（claims：`sub` = 使用者代號，加 companyId / roleId / departmentId 等）：

```java
JwtClaimsSet claims = JwtClaimsSet.builder()
		.subject(user.getUserId())
		.issuedAt(now).expiresAt(now.plusSeconds(expirationSeconds))
		.claim("companyId", user.getCompanyId())
		.claim("roleId", user.getRoleId())
		.build();
String token = jwtEncoder.encode(
		JwtEncoderParameters.from(JwsHeader.with(MacAlgorithm.HS256).build(), claims)).getTokenValue();
```

---

## 9. 稽核與日誌

### 9.1 業務操作稽核（寫 DB）

業務操作以 **AOP + 自訂 Annotation** 寫入專屬稽核表（對應 ifrs16web 的 `C_TransactionLog`）：

- 在 Controller/Service 方法標 `@LogAction("登入")`（動作字串為**中文語意，不帶模組代號**）。
- 對應 `@Aspect` 攔截，記錄：操作者、動作描述、IP、輸入/輸出（密碼類欄位**遮罩**）、結果（SUCCESS/FAIL）、耗時等。
- 失敗時於 `@AfterThrowing` / finally **仍寫入稽核**（result=FAIL）。
- 測試環境可用 `@Profile("!test")` 關閉切面。

### 9.2 應用程式日誌

- 框架：**Logback**（`logback-spring.xml`）+ SLF4J（Lombok `@Slf4j`）。**不用 Log4j**，不要雙軌。
- 輸出 Console + 每日滾動檔案；高吞吐用 `AsyncAppender`。
- 等級：`com.uitc` 於 dev 設 `DEBUG`、prod 設 `INFO`。
- 日誌路徑**依環境變數 / profile** 設定（不寫死於程式或設定檔）。

---

## 10. 建置與相依套件

### 10.1 Maven 與 Initializr 標準套件組

`groupId = com.uitc[.xxx]`、`artifactId` kebab-case、`<java.version>25</java.version>`、打包用 `spring-boot-maven-plugin`。

新專案以 Spring Initializr 產生，標準勾選（對應 Boot 4 artifact）：

| Initializr 名稱 | 用途 | artifactId（Boot 4） |
|-----------------|------|----------------------|
| Spring Web | 基礎 Web/MVC | `spring-boot-starter-webmvc` |
| Lombok | 簡化語法（1.18.64） | `org.projectlombok:lombok`（optional） |
| Spring REST Docs | API 文件 | `spring-boot-starter-restdocs`（test）。**Swagger UI 另加** `org.springdoc:springdoc-openapi-starter-webmvc-ui:3.0.3`（3.0.x 線對應 Boot 4） |
| Spring Data JPA | ORM（含 Hibernate） | `spring-boot-starter-data-jpa` |
| MS SQL Server Driver | 連 MSSQL | `com.microsoft.sqlserver:mssql-jdbc`（runtime） |
| Spring Boot DevTools | 開發熱重載 | `spring-boot-devtools`（runtime, optional） |
| Spring Security | 安全框架 | `spring-boot-starter-security` |
| Validation | 欄位驗證 | `spring-boot-starter-validation` |
| OAuth2 Resource Server | JWT 登入驗證 | `spring-boot-starter-security-oauth2-resource-server` |
| Spring Boot Actuator | 狀態監控 | `spring-boot-starter-actuator` |

> Swagger UI（`/swagger-ui/index.html`）、OpenAPI JSON（`/v3/api-docs`）由 springdoc 提供；記得在 `SecurityConfig` 放行其路徑（見 §8）。可加 `@OpenAPIDefinition` + `@SecurityScheme(type=HTTP, scheme="bearer")` 讓 Swagger「Authorize」可貼 JWT。

### 10.2 環境 Profile

Maven profile 對應 Spring profile（`dev` 預設 / `test` / `uat` / `prod`），以 `spring.profiles.active=@activatedProperties@` 帶入。

### 10.3 打包與部署

- 預設 **JAR + 內嵌 Tomcat**（`java -jar`）。
- 若部署到**外部 Tomcat**，才用 `war` + `extends SpringBootServletInitializer`；**Boot 4 外部 Tomcat 需 Tomcat 11+**。

---

## 11. 測試策略

| 項目 | 規範 |
|------|------|
| 框架 | **JUnit 6.1.0（Jupiter）** + **Mockito** |
| 重點 | **主寫 Service / Util 層單元測試**（純邏輯、mock 協作者），不以重量級整合測試為主 |
| 切片測試（輔助） | `@WebMvcTest` + `MockMvc` 測 Controller 契約；`@DataJpaTest` 測 DAO；安全契約用 `@SpringBootTest` + `MockMvc` |
| DB（測試） | H2 in-memory（`create-drop`）；對既有 DB 對映需注意 H2 會掩蓋欄位名不符（見 §7） |
| 命名 | `shouldXxx_whenYyy`；測試 package 與主程式一致 |

**Boot 4 測試切片註解套件已位移**（非舊 `org.springframework.boot.test.autoconfigure.*`）：

- `@DataJpaTest` → `org.springframework.boot.data.jpa.test.autoconfigure`
- `@WebMvcTest` / `@AutoConfigureMockMvc` → `org.springframework.boot.webmvc.test.autoconfigure`
- `@AutoConfigureTestDatabase` → `org.springframework.boot.jdbc.test.autoconfigure`
- `TestEntityManager` → `org.springframework.boot.jpa.test.autoconfigure`
- `@MockitoBean`（取代 `@MockBean`）→ `org.springframework.test.context.bean.override.mockito`

```java
@ExtendWith(MockitoExtension.class)
class AuthServiceTest {
	@Mock SUserDao sUserDao;
	@Mock JwtEncoder jwtEncoder;

	@Test
	void shouldThrow_whenPasswordWrong() {
		// given mock SUser ...
		assertThatThrownBy(() -> authService.login(new LoginReq("C1", "nkj", "wrong")))
				.isInstanceOf(AuthenticationFailedException.class);
	}
}
```

> 若採 test-first：先寫會失敗的測試（紅）→ 實作 → 轉綠 → 跑整套。

---

## 12. 新專案啟動 Checklist

- [ ] `groupId = com.uitc[.xxx]`，`artifactId` kebab-case；Java 25 + Spring Boot 4.0.6 + Maven
- [ ] Initializr 標準套件組（§10.1）；Swagger 另加 springdoc 3.0.x
- [ ] 套件分層 `controller.api → service → dao → entity`，`@Transactional` 在 Service（查詢 readOnly）
- [ ] Controller 以 ifrs16 代號（`AM1000Controller`）或語意名命名；**DTO / 稽核 / URL 不帶代號**
- [ ] DAO 命名 `*Dao extends JpaRepository`
- [ ] DTO 用 record + 語意命名；轉換用靜態 `parse()`
- [ ] Entity 對映既有表名/欄名（原樣）；設 `PhysicalNamingStrategyStandardImpl`、`ddl-auto=none`
- [ ] Controller 回 DTO/ResponseEntity + RESTful 動詞；全域 `@RestControllerAdvice` + RuntimeException
- [ ] Bean Validation（`jakarta.validation`）+ `@Valid`
- [ ] Spring Security 6 `SecurityFilterChain` + OAuth2 Resource Server（JWT/Nimbus，無狀態）；金鑰走環境變數
- [ ] AOP `@LogAction` 寫 DB 稽核表（中文語意動作字串）
- [ ] Logback 單軌；日誌路徑依環境變數
- [ ] constructor injection（`@RequiredArgsConstructor` + final；`@Value` 用顯式建構子）
- [ ] 縮排 Tab；中文 Javadoc；無死碼 / 無 `printStackTrace`
- [ ] JUnit 6.1.0 + Mockito；主寫 Service / Util 單元測試
