# ASP.NET Core minimal API (.NET 10)

Techniques verified in practice for the capabilities listed in the main guide §9.

| Capability | Technique |
|---|---|
| Field descriptions and examples | XML `<summary>` and `<example>` on DTO properties, read by the .NET 10 OpenAPI XML comment source generator |
| Parameter examples | The example attribute of `<param>` is not read. Declare a DTO for the input and put `<example>` on its properties |
| Operation summary, description, tags | `WithSummary`, `WithDescription`, `WithTags` |
| Response declarations | `Produces<T>(statusCode)` |
| Built-in error formats | `ProducesValidationProblem` and `ProducesProblem` declare the framework's problem-details format. Do not use them when the endpoint returns a custom error shape |
| File upload fields | Register a document transformer with `AddOpenApi(options => options.AddDocumentTransformer<T>())` that rewrites file array items into an inline `type: string, format: binary` schema, so Swagger UI shows a file picker |
| Document URL under a sub-path | Point Swagger UI at the document with a path relative to the UI page, such as `../openapi/v1.json` when the UI is served at `/swagger`, so it resolves under any sub-path |
