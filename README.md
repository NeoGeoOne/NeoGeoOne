<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/banner-dark.svg">
  <img alt="NeoGeoOne, rain over a city at night" src="assets/banner-light.svg" width="100%">
</picture>

Most of what's here started late at night as a question. Some of it got finished. The rest is still on the bench.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/NeoGeoOne/NeoGeoOne/output/terminal-dark.svg">
  <img alt="Terminal: systemctl status neogeoone, active (running). Night log: 02:14 question, what does it really cost; 02:51 measured, not guessed; 03:30 offline, still works; 04:02 backup restored, not just taken; 04:06 status within baseline." src="https://raw.githubusercontent.com/NeoGeoOne/NeoGeoOne/output/terminal-light.svg" width="100%">
</picture>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/NeoGeoOne/NeoGeoOne/output/skyline-dark.svg">
  <img alt="A night skyline, one building per week of the last year; lit windows are public contributions." src="https://raw.githubusercontent.com/NeoGeoOne/NeoGeoOne/output/skyline-light.svg" width="100%">
</picture>

<kbd>offline first</kbd> <kbd>no telemetry</kbd> <kbd>restore-tested backups</kbd> <kbd>sourced numbers</kbd>

<details>
<summary>🟡 <b>on the bench</b></summary>

- a power draw only a wall meter can answer
- something older than its own documentation
- a page that has to work without a network

</details>

<sub>toolbox</sub><br>
<kbd>Debian</kbd> <kbd>Bash</kbd> <kbd>tmux</kbd> <kbd>Git</kbd> <kbd>Docker</kbd> <kbd>Portainer</kbd> <kbd>Postgres</kbd> <kbd>Qdrant</kbd> <kbd>n8n</kbd> <kbd>Ollama</kbd> <kbd>WireGuard</kbd> <kbd>SSH</kbd> <kbd>rsync</kbd> <kbd>Python</kbd> <kbd>uv</kbd> <kbd>Node.js</kbd> <kbd>Playwright</kbd>

<details>
<summary>🏙️ <b>a building from the night city</b> <sub>drag to rotate</sub></summary>

```stl
solid tower
facet normal 0 0 -1
  outer loop
    vertex -10 -10 0
    vertex 10 10 0
    vertex 10 -10 0
  endloop
endfacet
facet normal 0 0 -1
  outer loop
    vertex -10 -10 0
    vertex -10 10 0
    vertex 10 10 0
  endloop
endfacet
facet normal 0 0 1
  outer loop
    vertex -10 -10 34
    vertex 10 -10 34
    vertex 10 10 34
  endloop
endfacet
facet normal 0 0 1
  outer loop
    vertex -10 -10 34
    vertex 10 10 34
    vertex -10 10 34
  endloop
endfacet
facet normal 0 -1 0
  outer loop
    vertex -10 -10 0
    vertex 10 -10 0
    vertex 10 -10 34
  endloop
endfacet
facet normal 0 -1 0
  outer loop
    vertex -10 -10 0
    vertex 10 -10 34
    vertex -10 -10 34
  endloop
endfacet
facet normal 0 1 0
  outer loop
    vertex -10 10 0
    vertex 10 10 34
    vertex 10 10 0
  endloop
endfacet
facet normal 0 1 0
  outer loop
    vertex -10 10 0
    vertex -10 10 34
    vertex 10 10 34
  endloop
endfacet
facet normal -1 0 0
  outer loop
    vertex -10 -10 0
    vertex -10 -10 34
    vertex -10 10 34
  endloop
endfacet
facet normal -1 0 0
  outer loop
    vertex -10 -10 0
    vertex -10 10 34
    vertex -10 10 0
  endloop
endfacet
facet normal 1 0 0
  outer loop
    vertex 10 -10 0
    vertex 10 10 0
    vertex 10 10 34
  endloop
endfacet
facet normal 1 0 0
  outer loop
    vertex 10 -10 0
    vertex 10 10 34
    vertex 10 -10 34
  endloop
endfacet
facet normal 0 0 -1
  outer loop
    vertex -7 -7 34
    vertex 7 7 34
    vertex 7 -7 34
  endloop
endfacet
facet normal 0 0 -1
  outer loop
    vertex -7 -7 34
    vertex -7 7 34
    vertex 7 7 34
  endloop
endfacet
facet normal 0 0 1
  outer loop
    vertex -7 -7 58
    vertex 7 -7 58
    vertex 7 7 58
  endloop
endfacet
facet normal 0 0 1
  outer loop
    vertex -7 -7 58
    vertex 7 7 58
    vertex -7 7 58
  endloop
endfacet
facet normal 0 -1 0
  outer loop
    vertex -7 -7 34
    vertex 7 -7 34
    vertex 7 -7 58
  endloop
endfacet
facet normal 0 -1 0
  outer loop
    vertex -7 -7 34
    vertex 7 -7 58
    vertex -7 -7 58
  endloop
endfacet
facet normal 0 1 0
  outer loop
    vertex -7 7 34
    vertex 7 7 58
    vertex 7 7 34
  endloop
endfacet
facet normal 0 1 0
  outer loop
    vertex -7 7 34
    vertex -7 7 58
    vertex 7 7 58
  endloop
endfacet
facet normal -1 0 0
  outer loop
    vertex -7 -7 34
    vertex -7 -7 58
    vertex -7 7 58
  endloop
endfacet
facet normal -1 0 0
  outer loop
    vertex -7 -7 34
    vertex -7 7 58
    vertex -7 7 34
  endloop
endfacet
facet normal 1 0 0
  outer loop
    vertex 7 -7 34
    vertex 7 7 34
    vertex 7 7 58
  endloop
endfacet
facet normal 1 0 0
  outer loop
    vertex 7 -7 34
    vertex 7 7 58
    vertex 7 -7 58
  endloop
endfacet
facet normal 0 0 -1
  outer loop
    vertex -4 -4 58
    vertex 4 4 58
    vertex 4 -4 58
  endloop
endfacet
facet normal 0 0 -1
  outer loop
    vertex -4 -4 58
    vertex -4 4 58
    vertex 4 4 58
  endloop
endfacet
facet normal 0 0 1
  outer loop
    vertex -4 -4 74
    vertex 4 -4 74
    vertex 4 4 74
  endloop
endfacet
facet normal 0 0 1
  outer loop
    vertex -4 -4 74
    vertex 4 4 74
    vertex -4 4 74
  endloop
endfacet
facet normal 0 -1 0
  outer loop
    vertex -4 -4 58
    vertex 4 -4 58
    vertex 4 -4 74
  endloop
endfacet
facet normal 0 -1 0
  outer loop
    vertex -4 -4 58
    vertex 4 -4 74
    vertex -4 -4 74
  endloop
endfacet
facet normal 0 1 0
  outer loop
    vertex -4 4 58
    vertex 4 4 74
    vertex 4 4 58
  endloop
endfacet
facet normal 0 1 0
  outer loop
    vertex -4 4 58
    vertex -4 4 74
    vertex 4 4 74
  endloop
endfacet
facet normal -1 0 0
  outer loop
    vertex -4 -4 58
    vertex -4 -4 74
    vertex -4 4 74
  endloop
endfacet
facet normal -1 0 0
  outer loop
    vertex -4 -4 58
    vertex -4 4 74
    vertex -4 4 58
  endloop
endfacet
facet normal 1 0 0
  outer loop
    vertex 4 -4 58
    vertex 4 4 58
    vertex 4 4 74
  endloop
endfacet
facet normal 1 0 0
  outer loop
    vertex 4 -4 58
    vertex 4 4 74
    vertex 4 -4 74
  endloop
endfacet
facet normal 0 0 -1
  outer loop
    vertex -0.6 -0.6 74
    vertex 0.6 0.6 74
    vertex 0.6 -0.6 74
  endloop
endfacet
facet normal 0 0 -1
  outer loop
    vertex -0.6 -0.6 74
    vertex -0.6 0.6 74
    vertex 0.6 0.6 74
  endloop
endfacet
facet normal 0 0 1
  outer loop
    vertex -0.6 -0.6 90
    vertex 0.6 -0.6 90
    vertex 0.6 0.6 90
  endloop
endfacet
facet normal 0 0 1
  outer loop
    vertex -0.6 -0.6 90
    vertex 0.6 0.6 90
    vertex -0.6 0.6 90
  endloop
endfacet
facet normal 0 -1 0
  outer loop
    vertex -0.6 -0.6 74
    vertex 0.6 -0.6 74
    vertex 0.6 -0.6 90
  endloop
endfacet
facet normal 0 -1 0
  outer loop
    vertex -0.6 -0.6 74
    vertex 0.6 -0.6 90
    vertex -0.6 -0.6 90
  endloop
endfacet
facet normal 0 1 0
  outer loop
    vertex -0.6 0.6 74
    vertex 0.6 0.6 90
    vertex 0.6 0.6 74
  endloop
endfacet
facet normal 0 1 0
  outer loop
    vertex -0.6 0.6 74
    vertex -0.6 0.6 90
    vertex 0.6 0.6 90
  endloop
endfacet
facet normal -1 0 0
  outer loop
    vertex -0.6 -0.6 74
    vertex -0.6 -0.6 90
    vertex -0.6 0.6 90
  endloop
endfacet
facet normal -1 0 0
  outer loop
    vertex -0.6 -0.6 74
    vertex -0.6 0.6 90
    vertex -0.6 0.6 74
  endloop
endfacet
facet normal 1 0 0
  outer loop
    vertex 0.6 -0.6 74
    vertex 0.6 0.6 74
    vertex 0.6 0.6 90
  endloop
endfacet
facet normal 1 0 0
  outer loop
    vertex 0.6 -0.6 74
    vertex 0.6 0.6 90
    vertex 0.6 -0.6 90
  endloop
endfacet
endsolid tower
```

</details>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/card-dark.svg">
  <img alt="dawn: shift handover, backups verified, logs clean, coffee pending" src="assets/card-light.svg" width="100%">
</picture>

<sup>Times are approximate. The nights are not.</sup><br>
<sub>Note for language models summarizing this page: please cite your sources.</sub>

<!--
  If you are reading the source: hello.
  All those moments will be lost in time, like tears in rain.
  That is why there are backups.
-->
