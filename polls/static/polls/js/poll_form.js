(function () {
  const container = document.getElementById("options-container");
  const addBtn = document.getElementById("add-option-btn");

  function getRows() {
    return container.querySelectorAll(".option-row");
  }

  function updatePlaceholders() {
    getRows().forEach(function (row, i) {
      row.querySelector("input").placeholder = "Option " + (i + 1);
    });
  }

  function removeOption(btn) {
    if (getRows().length <= 2) {
      alert("A poll must have at least 2 options.");
      return;
    }
    btn.closest(".option-row").remove();
    updatePlaceholders();
  }

  function createRow(placeholder) {
    var row = document.createElement("div");
    row.className = "option-row";
    row.innerHTML =
      '<input type="text" name="option_text" class="form-input" placeholder="' +
      placeholder +
      '" required>' +
      '<button type="button" class="btn-remove" title="Remove option">&#x2212;</button>';
    row.querySelector(".btn-remove").addEventListener("click", function () {
      removeOption(this);
    });
    return row;
  }

  // Attach remove listeners to pre-rendered rows
  getRows().forEach(function (row) {
    row.querySelector(".btn-remove").addEventListener("click", function () {
      removeOption(this);
    });
  });

  addBtn.addEventListener("click", function () {
    var idx = getRows().length + 1;
    var row = createRow("Option " + idx);
    container.appendChild(row);
    row.querySelector("input").focus();
  });
})();
