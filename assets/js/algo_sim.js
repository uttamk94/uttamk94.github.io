/* ===== Algorithm Simulation Engine =====
 * Renders traces recorded by the build pipeline. Each step is a full state
 * snapshot (data + highlights + caption), so stepping/rewinding is trivial.
 * Supported renderers: array, board, graph, grid, tree.
 * The page loads this file then calls AlgoSim.init() (no arguments); the fixed
 * element ids below are expected on the page.
 */
(function (window) {
  'use strict';

  var State = {
    steps: [],
    index: 0,
    playing: false,
    timer: null,
    speed: 4
  };

  function $(id) { return document.getElementById(id); }

  /* ----- framework ----- */

  function bindControls() {
    var stepBtn = $('simStep');
    var prevBtn = $('simPrev');
    var resetBtn = $('simReset');
    var playBtn = $('simPlay');
    var speedEl = $('simSpeed');
    if (stepBtn) stepBtn.addEventListener('click', function () { pause(); next(); });
    if (prevBtn) prevBtn.addEventListener('click', function () { pause(); back(); });
    if (resetBtn) resetBtn.addEventListener('click', function () { pause(); reset(); });
    if (playBtn) playBtn.addEventListener('click', togglePlay);
    if (speedEl) speedEl.addEventListener('input', function (e) {
      State.speed = parseInt(e.target.value, 10) || 4;
      updateTimer();
    });
  }

  function init() {
    var dataEl = $('simData');
    if (!dataEl) return;
    try {
      State.steps = JSON.parse(dataEl.textContent);
    } catch (e) {
      State.steps = [];
    }
    bindControls();
    reset();
  }

  function delayMs() {
    var base = 1100;   /* ms at speed 1 */
    return Math.max(30, base / State.speed);
  }

  function updateTimer() {
    if (!State.playing) return;
    if (State.timer) clearInterval(State.timer);
    State.timer = setInterval(function () {
      if (State.index >= State.steps.length - 1) { pause(); return; }
      next();
    }, delayMs());
  }

  function play() {
    if (State.steps.length <= 1) return;
    State.playing = true;
    if ($('simPlay')) $('simPlay').textContent = '⏸ Pause';
    updateTimer();
  }

  function pause() {
    State.playing = false;
    if (State.timer) { clearInterval(State.timer); State.timer = null; }
    if ($('simPlay')) $('simPlay').textContent = '▶ Play';
  }

  function togglePlay() {
    if (State.playing) pause(); else play();
  }

  function reset() {
    State.index = 0;
    render();
  }

  function next() {
    if (State.index < State.steps.length - 1) { State.index++; render(); }
  }

  function back() {
    if (State.index > 0) { State.index--; render(); }
    if (State.index === 0) pause();
  }
  /* ----- dispatch ----- */

  function render() {
    var stepData = State.steps[State.index];
    var stage = $('simStage');
    if (!stage) return;
    stage.innerHTML = '';
    if (!stepData) return;

    var kind = stepData.kind || 'array';
    if (kind === 'array') renderArray(stage, stepData);
    else if (kind === 'board') renderBoard(stage, stepData);
    else if (kind === 'graph') renderGraph(stage, stepData);
    else if (kind === 'grid') renderGrid(stage, stepData);
    else if (kind === 'tree') renderTree(stage, stepData);

    var caption = $('simCaption');
    if (caption) caption.textContent = (stepData.caption || '');
    var counter = $('simCounter');
    if (counter) counter.textContent = State.index + ' / ' + (State.steps.length - 1);
    updateLegend(stepData);
  }

  function updateLegend(stepData) {
    var legend = $('simLegend');
    if (!legend) return;
    var kind = stepData.kind || 'array';
    var items = [];
    if (kind === 'array') {
      items = [
        ['swatch cmp', 'comparing'], ['swatch swp', 'swapped/moving'],
        ['swatch cur', 'current/pivot'], ['swatch mark', 'lo / hi / mid pointers']
      ];
    } else if (kind === 'graph') {
      items = [
        ['swatch cur', 'current'], ['swatch front', 'frontier'],
        ['swatch done', 'finalised'], ['swatch path', 'path edge']
      ];
    } else if (kind === 'board') {
      items = [['swatch queen', 'queen'], ['swatch last', 'just placed'], ['swatch conf', 'in conflict']];
    } else if (kind === 'grid') {
      items = [['swatch cur', 'current cell'], ['swatch fill', 'filled/computed']];
    } else if (kind === 'tree') {
      items = [['swatch cur', 'current'], ['swatch done', 'processed'], ['swatch path', 'path']];
    }
    if (!items.length) { legend.style.display = 'none'; return; }
    legend.style.display = 'flex';
    legend.innerHTML = items.map(function (it) {
      return '<span class="legend-item"><span class="' + it[0] + '"></span>' + it[1] + '</span>';
    }).join('');
  }

  function toSet(arr) {
    var s = {};
    (arr || []).forEach(function (x) { s['' + x] = true; });
    return s;
  }

  /* ----- array renderer ----- */

  function renderArray(stage, step) {
    var data = step.data || [];
    var max = 1;
    for (var i = 0; i < data.length; i++) if (data[i] > max) max = data[i];

    var highlight = toSet(step.highlights);
    var compare = toSet(step.compare);
    var swap = toSet(step.swap);
    var markers = step.markers || {};

    var wrap = document.createElement('div');
    wrap.className = 'algo-array';
    if (step.done) wrap.classList.add('done');

    for (var k = 0; k < data.length; k++) {
      var col = document.createElement('div');
      col.className = 'algo-bar-col';
      var bar = document.createElement('div');
      bar.className = 'algo-bar';
      bar.style.height = Math.round((data[k] / max) * 100) + '%';
      if (highlight.has('' + k)) bar.classList.add('cur');
      if (compare.has('' + k)) bar.classList.add('cmp');
      if (swap.has('' + k)) bar.classList.add('swp');
      var val = document.createElement('div');
      val.className = 'algo-bar-val';
      val.textContent = data[k];

      var ptr = document.createElement('div');
      ptr.className = 'algo-bar-ptr';
      var labels = [];
      if (markers.lo === k) labels.push('lo');
      if (markers.mid === k) labels.push('mid');
      if (markers.hi === k) labels.push('hi');
      ptr.textContent = labels.join(' ');

      var idx = document.createElement('div');
      idx.className = 'algo-bar-idx';
      idx.textContent = k;

      col.appendChild(bar);
      col.appendChild(val);
      col.appendChild(ptr);
      col.appendChild(idx);
      wrap.appendChild(col);
    }
    stage.appendChild(wrap);
  }


  /* ----- board renderer (N-Queens; also handles Sudoku via step.cells) ----- */

  function renderBoard(stage, step) {
    var n = step.n || 8;
    var isSudoku = !!step.cells;
    var grid = document.createElement('div');
    grid.className = 'algo-board' + (isSudoku ? ' sudoku' : '');
    grid.style.gridTemplateColumns = 'repeat(' + n + ', 1fr)';
    var conf = toSet((step.conflict || []).map(function (p) { return (p[0] * 1000 + p[1]); }));
    for (var r = 0; r < n; r++) {
      for (var c = 0; c < n; c++) {
        var cell = document.createElement('div');
        cell.className = 'algo-cell' + ((r + c) % 2 === 0 ? ' dark' : ' light');
        if (isSudoku) {
          var v = step.cells[r] && step.cells[r][c];
          if (v) {
            cell.textContent = String(v);
            cell.classList.add(step.given && step.given[r] && step.given[r][c] ? 'given' : 'filled');
          }
          if (c % 3 === 0) cell.classList.add('edge-l');
          if (r % 3 === 0) cell.classList.add('edge-t');
        } else {
          var hasQueen = step.queens[r] === c;
          if (hasQueen) {
            cell.classList.add('queen');
            cell.textContent = '\u2655';
          }
        }
        if (step.last && step.last[0] === r && step.last[1] === c) cell.classList.add('last');
        if (conf.has('' + (r * 1000 + c))) cell.classList.add('conflict');
        grid.appendChild(cell);
      }
    }
    if (step.done) grid.classList.add('done');
    stage.appendChild(grid);
  }

  /* ----- graph renderer (e.g. Dijkstra) ----- */

  function renderGraph(stage, step) {
    var NS = 'http://www.w3.org/2000/svg';
    var svg = document.createElementNS(NS, 'svg');
    svg.setAttribute('viewBox', '0 0 560 270');
    svg.setAttribute('class', 'algo-graph');
    var W = 560, H = 270, M = 28;

    var edges = step.edges || [];
    var nodes = step.nodes || [];
    var dist = step.dist || [];
    var byId = {};
    nodes.forEach(function (nd) { byId[nd.id] = nd; });

    /* draw edges first (under nodes) */
    edges.forEach(function (e) {
      var a = byId[e.from], b = byId[e.to];
      if (!a || !b) return;
      var line = document.createElementNS(NS, 'line');
      line.setAttribute('x1', a.x);
      line.setAttribute('y1', a.y);
      line.setAttribute('x2', b.x);
      line.setAttribute('y2', b.y);
      line.setAttribute('class', 'g-edge ' + (e.state || 'normal'));
      svg.appendChild(line);
      if (step.directed) {
        /* arrowhead pointing into b, stopped at the node's rim */
        var dx = b.x - a.x, dy = b.y - a.y;
        var len = Math.sqrt(dx * dx + dy * dy) || 1;
        var ux = dx / len, uy = dy / len;
        var tx = b.x - ux * 17, ty = b.y - uy * 17;
        var px = -uy, py = ux;
        var tri = document.createElementNS(NS, 'polygon');
        var p1 = tx + ',' + ty;
        var p2 = (tx - ux * 9 + px * 4.5) + ',' + (ty - uy * 9 + py * 4.5);
        var p3 = (tx - ux * 9 - px * 4.5) + ',' + (ty - uy * 9 - py * 4.5);
        tri.setAttribute('points', p1 + ' ' + p2 + ' ' + p3);
        tri.setAttribute('class', 'g-arrow ' + (e.state || 'normal'));
        svg.appendChild(tri);
      }
      var mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2;
      var tw = document.createElementNS(NS, 'text');
      tw.setAttribute('x', mx);
      tw.setAttribute('y', my - 4);
      tw.setAttribute('class', 'g-weight');
      tw.textContent = e.weight;
      svg.appendChild(tw);
    });

    nodes.forEach(function (nd) {
      var g = document.createElementNS(NS, 'g');
      var circle = document.createElementNS(NS, 'circle');
      circle.setAttribute('cx', nd.x);
      circle.setAttribute('cy', nd.y);
      circle.setAttribute('r', M - 6);
      circle.setAttribute('class', 'g-node ' + (nd.state || 'unvisited'));
      g.appendChild(circle);
      var label = document.createElementNS(NS, 'text');
      label.setAttribute('x', nd.x);
      label.setAttribute('y', nd.y + 4);
      label.setAttribute('class', 'g-label');
      label.textContent = nd.label;
      g.appendChild(label);
      var d = dist[nd.id];
      if (d !== undefined) {
        var dlab = document.createElementNS(NS, 'text');
        dlab.setAttribute('x', nd.x);
        dlab.setAttribute('y', nd.y + 22);
        dlab.setAttribute('class', 'g-dist');
        dlab.textContent = 'd=' + d;
        g.appendChild(dlab);
      }
      svg.appendChild(g);
    });
    stage.appendChild(svg);
  }


  /* ----- grid renderer (DP tables) ----- */

  function renderGrid(stage, step) {
    var matrix = step.matrix || step.grid || [];
    var table = document.createElement('table');
    table.className = 'algo-grid';
    var current = step.current;
    var fill = toSet((step.fill || []).map(function (p) { return (p[0] * 1000 + p[1]); }));
    for (var r = 0; r < matrix.length; r++) {
      var tr = document.createElement('tr');
      for (var c = 0; c < matrix[r].length; c++) {
        var td = document.createElement('td');
        var v = matrix[r][c];
        td.textContent = (v === null || v === undefined) ? '' : v;
        if (current && current[0] === r && current[1] === c) td.classList.add('cur');
        if (fill.has('' + (r * 1000 + c))) td.classList.add('fill');
        tr.appendChild(td);
      }
      table.appendChild(tr);
    }
    stage.appendChild(table);
  }

  /* ----- tree renderer ----- */

  function renderTree(stage, step) {
    var NS = 'http://www.w3.org/2000/svg';
    var nodes = (step.tree || step.nodes || []);
    if (!nodes.length) { stage.textContent = 'No tree data.'; return; }
    var byId = {};
    var children = {};
    var levels = {};
    nodes.forEach(function (nd) { byId[nd.id] = nd; children[nd.id] = []; });
    nodes.forEach(function (nd) {
      if (nd.parent !== null && nd.parent !== undefined && byId[nd.parent]) {
        children[nd.parent].push(nd.id);
      }
    });
    var root = nodes.filter(function (nd) { return nd.parent === null || nd.parent === undefined; })[0];
    if (!root) root = nodes[0];

    var xpos = {};
    var counter = 0;
    function assign(id) {
      (children[id] || []).forEach(assign);
      xpos[id] = counter++;
    }
    levels[root.id] = 0;
    (function levelit(id, lv) {
      (children[id] || []).forEach(function (ch) { levels[ch] = lv + 1; levelit(ch, lv + 1); });
    })(root.id, 0);
    assign(root.id);

    var W = 560, H = 200, M = 24;
    var svg = document.createElementNS(NS, 'svg');
    svg.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
    svg.setAttribute('class', 'algo-tree');
    var total = counter;

    nodes.forEach(function (nd) {
      if (nd.parent === null || nd.parent === undefined || !byId[nd.parent]) return;
      var a = byId[nd.parent];
      var x1 = (xpos[a.id] + 0.5) * (W / total);
      var y1 = (levels[a.id] + 0.5) * (H / (maxLevel() + 1));
      var x2 = (xpos[nd.id] + 0.5) * (W / total);
      var y2 = (levels[nd.id] + 0.5) * (H / (maxLevel() + 1));
      var line = document.createElementNS(NS, 'line');
      line.setAttribute('x1', x1); line.setAttribute('y1', y1);
      line.setAttribute('x2', x2); line.setAttribute('y2', y2);
      line.setAttribute('class', 't-edge ' + (nd.edgeState || (nd.state === 'path' ? 'path' : 'normal')));
      svg.appendChild(line);
    });

    function maxLevel() {
      var m = 0;
      nodes.forEach(function (nd) { if ((levels[nd.id] || 0) > m) m = levels[nd.id]; });
      return m;
    }

    nodes.forEach(function (nd) {
      var g = document.createElementNS(NS, 'g');
      var cx = (xpos[nd.id] + 0.5) * (W / total);
      var cy = (levels[nd.id] + 0.5) * (H / (maxLevel() + 1));
      var circle = document.createElementNS(NS, 'circle');
      circle.setAttribute('cx', cx); circle.setAttribute('cy', cy);
      circle.setAttribute('r', M - 6);
      circle.setAttribute('class', 'g-node ' + (nd.state || 'normal'));
      g.appendChild(circle);
      var label = document.createElementNS(NS, 'text');
      label.setAttribute('x', cx); label.setAttribute('y', cy + 4);
      label.setAttribute('class', 'g-label');
      label.textContent = (nd.value !== undefined && nd.value !== null) ? nd.value : nd.label;
      g.appendChild(label);
      svg.appendChild(g);
    });

    stage.appendChild(svg);
  }

  window.AlgoSim = { init: init };
})(window);

