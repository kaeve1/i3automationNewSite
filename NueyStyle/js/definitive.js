/* Domino feedback adapted from the earlier i3 site. */
(() => {
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const fine = matchMedia('(hover: hover) and (pointer: fine)');
  document.querySelectorAll('[data-domino]').forEach(grid => {
    const tiles = [...grid.children];
    const spread = origin => tiles.forEach((tile, i) => tile.style.setProperty('--d', origin < 0 ? 99 : Math.abs(i - origin)));
    grid.addEventListener('pointerover', event => {
      if(reduced.matches || !fine.matches) return;
      const tile = event.target.closest('[data-i]');
      if(tile && tile.parentElement === grid) spread(Number(tile.dataset.i));
    });
    grid.addEventListener('pointerleave', () => spread(-1));
    reduced.addEventListener('change', () => spread(-1));
  });
})();
