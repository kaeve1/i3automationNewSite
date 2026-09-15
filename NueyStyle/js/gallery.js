/* i3Automations - NueyStyle
   Gallery: balances the plates across 1, 2 or 3 columns by aspect ratio. */

(function () {
  "use strict";

  var mosaic = document.querySelector("[data-mosaic]");
  if (!mosaic) return;

  var columns = [].slice.call(mosaic.children);
  if (!columns.length) return;

  var plates = [].slice.call(mosaic.querySelectorAll(".plate")).sort(function (a, b) {
    return (a.getAttribute("data-order") | 0) - (b.getAttribute("data-order") | 0);
  });
  if (!plates.length) return;

  var CAPTION = 0.18;

  var wanted = function () {
    var width = window.innerWidth || document.documentElement.clientWidth;
    return width <= 700 ? 1 : (width <= 1100 ? 2 : 3);
  };

  var current = parseInt(mosaic.getAttribute("data-columns"), 10) || columns.length;

  var layout = function (count) {
    if (count === current) return;
    current = count;
    mosaic.setAttribute("data-columns", count);

    var heights = [];
    var i;
    for (i = 0; i < columns.length; i++) {
      columns[i].style.display = i < count ? "" : "none";
      if (i < count) {
        while (columns[i].firstChild) columns[i].removeChild(columns[i].firstChild);
        heights.push(0);
      }
    }

    for (i = 0; i < plates.length; i++) {
      var shortest = 0;
      var j;
      for (j = 1; j < heights.length; j++) if (heights[j] < heights[shortest]) shortest = j;
      columns[shortest].appendChild(plates[i]);
      var ratio = parseFloat(plates[i].getAttribute("data-ar")) || 1;
      heights[shortest] += 1 / ratio + CAPTION;
    }
  };

  var pending = false;
  var request = function () {
    if (pending) return;
    pending = true;
    window.requestAnimationFrame(function () {
      pending = false;
      layout(wanted());
    });
  };

  window.addEventListener("resize", request);
  window.addEventListener("orientationchange", request);
  layout(wanted());
})();
