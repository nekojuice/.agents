#!/usr/bin/env node
// Assemble a flat Thought Palette draft.json into an import-ready Library[] JSON.
// Usage: node assemble.mjs <draft.json> [output.json]   (default: import.json beside draft)
// Node fallback for assemble.py; must produce identical output. See SCHEMA.md.
import { readFileSync, writeFileSync } from 'node:fs'
import { dirname, join } from 'node:path'

const PROTECTED = ['未分類', '通用']
const HEX_RE = /^#[0-9A-Fa-f]{6}$/
const SLUG_RE = /^[a-z0-9-]+$/
const isNum = (v) => typeof v === 'number' && Number.isFinite(v)

function main(argv) {
  if (argv.length < 3) {
    console.error('Usage: node assemble.mjs <draft.json> [output.json]')
    return 2
  }
  const draftPath = argv[2]
  const outPath = argv[3] || join(dirname(draftPath), 'import.json')
  const draft = JSON.parse(readFileSync(draftPath, 'utf-8'))
  const errors = []
  const warnings = []

  const library = draft.library || 'Analysis'
  const elements = draft.elements || []
  const palettes = draft.palettes || []

  const eleById = new Map()
  for (let i = 0; i < elements.length; i++) {
    const e = elements[i]
    const eid = e.id
    if (!eid) { errors.push(`elements[${i}] missing id`); continue }
    if (eleById.has(eid)) errors.push(`duplicate element id '${eid}'`)
    if (!SLUG_RE.test(String(eid))) warnings.push(`element id '${eid}' is not a latin slug [a-z0-9-]`)
    if (!e.text) warnings.push(`element '${eid}' has empty text`)
    if (!e.storage_cat) warnings.push(`element '${eid}' has no storage_cat; filed under 未分類`)
    eleById.set(eid, e)
  }

  const referenced = new Set()

  const order = [...PROTECTED]
  const buckets = new Map(PROTECTED.map((n) => [n, []]))
  for (const e of elements) {
    if (!e.id) continue
    const cat = e.storage_cat || '未分類'
    if (!buckets.has(cat)) { buckets.set(cat, []); order.push(cat) }
    buckets.get(cat).push({ ele_id: e.id, text: e.text || '' })
  }
  const storageElement = order.map((name, i) => ({
    cat_id: `scat-${i + 1}`, cat_name: name, cat_ele: buckets.get(name),
  }))

  const paletas = []
  palettes.forEach((p, pi) => {
    const pname = p.name || `Palette ${pi + 1}`
    const uCat = { cat_id: `pcat-${pi + 1}-u`, cat_name: '未分類', cat_base: 0, cat_factor: 1, cat_ele: [] }
    const gCat = { cat_id: `pcat-${pi + 1}-g`, cat_name: '通用', cat_base: 0, cat_factor: 1, cat_color: '#FFFFFF', cat_ele: [] }
    const protectedTargets = { 未分類: uCat, 通用: gCat }
    const outCats = [uCat, gCat]
    const seenInPalette = new Set()

    ;(p.cats || []).forEach((c, ci) => {
      const cname = c.name || `cat ${ci + 1}`
      let base = c.base ?? 0
      let factor = c.factor ?? 1
      if (!isNum(base)) { errors.push(`palette '${pname}' cat '${cname}' base is not numeric`); base = 0 }
      if (!isNum(factor)) { errors.push(`palette '${pname}' cat '${cname}' factor is not numeric`); factor = 1 }
      if (isNum(base) && base < 0) warnings.push(`palette '${pname}' cat '${cname}' has negative base (${base})`)

      const refs = []
      for (const pl of c.elements || []) {
        const ele = pl.ele
        if (!eleById.has(ele)) { errors.push(`palette '${pname}' cat '${cname}' references unknown element '${ele}'`); continue }
        if (seenInPalette.has(ele)) { errors.push(`palette '${pname}' references element '${ele}' more than once`); continue }
        seenInPalette.add(ele)
        referenced.add(ele)
        let val = pl.val ?? 0
        if (!isNum(val)) { errors.push(`palette '${pname}' cat '${cname}' element '${ele}' val is not numeric`); val = 0 }
        else if (val < -5 || val > 5) warnings.push(`palette '${pname}' cat '${cname}' element '${ele}' val ${val} outside -5..+5`)
        refs.push({ ele_id: ele, val, index: refs.length })
      }

      let color = c.color ?? null
      if (color !== null && !HEX_RE.test(String(color))) {
        errors.push(`palette '${pname}' cat '${cname}' color '${color}' is not #RRGGBB`); color = null
      }

      if (protectedTargets[cname]) {
        const target = protectedTargets[cname]
        target.cat_base = base
        target.cat_factor = factor
        if (cname === '未分類' && color) target.cat_color = color
        for (const r of refs) { r.index = target.cat_ele.length; target.cat_ele.push(r) }
        return
      }

      const cat = { cat_id: `pcat-${pi + 1}-${ci + 1}`, cat_name: cname, cat_base: base, cat_factor: factor, cat_ele: refs }
      if (color) cat.cat_color = color
      outCats.push(cat)
    })

    if (!gCat.cat_ele.length) warnings.push(`palette '${pname}' has an empty 通用 cat; consider cross-cutting elements (documentation health, conventions, DX)`)

    const named = outCats.filter((c) => !PROTECTED.includes(c.cat_name))
    if (named.length > 21) errors.push(`palette '${pname}' has ${named.length} named cats (max 21)`)
    else if (named.length > 11) warnings.push(`palette '${pname}' has ${named.length} named cats (>11 may fatigue the user)`)

    const metadata = { ...p.metadata }
    if (p.kind) metadata.kind = p.kind
    const groups = {}
    for (const c of p.cats || []) if (c.group) groups[c.name] = c.group
    if (Object.keys(groups).length && metadata.cat_groups === undefined) metadata.cat_groups = groups

    paletas.push({ pal_id: `pal-${pi + 1}`, pal_name: pname, metadata, cats: outCats })
  })

  for (const eid of eleById.keys()) if (!referenced.has(eid)) warnings.push(`element '${eid}' is not referenced by any palette`)

  const lib = { storage_id: 'lib-1', storage_name: library, storage_element: storageElement, paletas }
  const output = [lib]

  report(errors, warnings, output)
  if (errors.length) { console.error(`\nNOT written: resolve ${errors.length} error(s) first.`); return 1 }
  writeFileSync(outPath, JSON.stringify(output, null, 2), 'utf-8')
  console.log(`\nWrote ${outPath}`)
  return 0
}

function report(errors, warnings, output) {
  const lib = output[0]
  console.log('=== Thought Palette assembly ===')
  console.log(`library: ${lib.storage_name}`)
  console.log(`storage cats: ${lib.storage_element.length}, elements: ${lib.storage_element.reduce((a, c) => a + c.cat_ele.length, 0)}`)
  for (const p of lib.paletas) {
    const named = p.cats.filter((c) => !PROTECTED.includes(c.cat_name))
    console.log(`palette '${p.pal_name}' (${p.metadata.kind || '-'}): ${named.length} named cats, ${p.cats.reduce((a, c) => a + c.cat_ele.length, 0)} refs`)
  }
  if (warnings.length) { console.log(`\n${warnings.length} WARNING(s):`); for (const w of warnings) console.log(`  ! ${w}`) }
  if (errors.length) { console.log(`\n${errors.length} ERROR(s):`); for (const e of errors) console.log(`  x ${e}`) }
  if (!errors.length && !warnings.length) console.log('no issues.')
}

process.exit(main(process.argv))
