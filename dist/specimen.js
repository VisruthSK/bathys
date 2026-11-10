"use strict";

const byId = (id) => document.getElementById(id);
const data = BATHYS_SPECIMEN;
const editor = byId("type");
const tester = document.querySelector(".tester");

function bindControl(id, defaultValue, render) {
  const slider = byId(id);
  const field = byId(`${id}Value`);
  const initialMin = slider.min;
  const initialMax = slider.max;
  const control = { value: defaultValue, reset };

  function set(value, writeField) {
    control.value = value;
    slider.min = String(Math.min(Number(slider.min), value));
    slider.max = String(Math.max(Number(slider.max), value));
    slider.value = String(value);
    if (writeField) field.value = String(value);
  }

  function reset() {
    slider.min = initialMin;
    slider.max = initialMax;
    set(defaultValue, true);
  }

  slider.addEventListener("input", () => {
    set(Math.round(Number(slider.value) * 100) / 100, true);
    render();
  });
  slider.addEventListener("dblclick", () => {
    reset();
    render();
  });
  field.addEventListener("input", () => {
    if (Number.isFinite(field.valueAsNumber) && field.validity.valid) {
      set(field.valueAsNumber, false);
      render();
    }
  });
  field.addEventListener("change", () => {
    let value = Number.isFinite(field.valueAsNumber)
      ? field.valueAsNumber
      : control.value;
    if (field.min !== "") value = Math.max(Number(field.min), value);
    if (field.max !== "") value = Math.min(Number(field.max), value);
    set(value, true);
    render();
  });
  field.addEventListener("keydown", (event) => {
    if (event.key === "Enter") field.blur();
  });
  reset();
  return control;
}

const controls = {
  size: bindControl("size", 64, update),
  width: bindControl("width", 100, update),
  tracking: bindControl("tracking", 0, update),
  glyphSize: bindControl("glyphSize", 255, updateGlyph),
};

function fitEditor() {
  editor.style.height = "auto";
  editor.style.height = `${Math.max(230, Math.min(850, editor.scrollHeight))}px`;
}

function update() {
  const small = byId("smallcaps").checked;
  const joins = byId("liga").checked;
  tester.style.setProperty("--type-size", `${controls.size.value}pt`);
  tester.style.setProperty("--width", controls.width.value);
  tester.style.setProperty("--tracking", `${controls.tracking.value}px`);
  tester.style.setProperty(
    "--features",
    [
      `"liga" ${Number(joins)}`,
      `"calt" ${Number(joins)}`,
      `"dlig" ${Number(byId("dlig").checked)}`,
      `"smcp" ${Number(small)}`,
      `"c2sc" ${Number(small)}`,
      '"kern" 1',
    ].join(", "),
  );
  fitEditor();
}

function updateGlyph() {
  byId("glyphView").textContent = byId("glyph").value;
  byId("glyphView").style.fontSize = `${controls.glyphSize.value}pt`;
}

for (const id of ["liga", "dlig", "smallcaps"])
  byId(id).addEventListener("input", update);
editor.addEventListener("input", fitEditor);
byId("glyph").addEventListener("input", updateGlyph);
byId("theme").addEventListener("click", () => {
  const dark = document.body.classList.toggle("dark");
  byId("theme").setAttribute("aria-pressed", String(dark));
});
byId("reset").addEventListener("click", () => {
  for (const id of ["size", "width", "tracking"]) controls[id].reset();
  byId("liga").checked = true;
  byId("dlig").checked = false;
  byId("smallcaps").checked = false;
  update();
});

function node(tag, className, text) {
  const element = document.createElement(tag);
  element.className = className;
  element.textContent = text;
  return element;
}

function showLigatures(catalogue, target, optional) {
  for (const word of catalogue) {
    const card = node("div", "pair", "");
    card.append(
      node("small", "", word),
      node("span", optional ? "font joined optional" : "font joined", word),
    );
    byId(target).append(card);
  }
}

showLigatures(data.standard, "pairs", false);
showLigatures(["BA", "NN", "EY", "TH", "WT", "EA"], "featuredPairs", false);
showLigatures(data.optional, "optionalPairs", true);
byId("standardCount").textContent = `(${data.standard.length})`;
byId("version").textContent = data.version;
update();
updateGlyph();
document.fonts.ready.then(fitEditor);
