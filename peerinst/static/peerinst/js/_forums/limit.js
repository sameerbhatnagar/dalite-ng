export function limitFileSize() {
  const pdfForm = document.getElementById("id_pdf");
  const warning = document.getElementById("warning");
  pdfForm.setAttribute("accept", ".pdf");
  pdfForm.onchange = function () {
    const fileSize = pdfForm.files[0].size;
    if (fileSize > 2000000) {
      window.alert(`File too big: ${fileSize / 1000}kB`);
      warning.style.display = "inline";
      $(".mdc-button").each(
        /* @this */ function () {
          $(this).attr("disabled", true);
        },
      );
    } else {
      warning.style.display = "none";
      $(".mdc-button").each(
        /* @this */ function () {
          $(this).attr("disabled", false);
        },
      );
    }
    return;
  };
}
