const autoprefixer = require("autoprefixer");
const babel = require("rollup-plugin-babel");
const buffer = require("vinyl-buffer");
const commonjs = require("rollup-plugin-commonjs");
const concat = require("gulp-concat");
const gulp = require("gulp");
const merge = require("merge-stream");
const postcss = require("gulp-postcss");
const rename = require("gulp-rename");
const rollup = require("rollup-stream");
const resolve = require("rollup-plugin-node-resolve");
const sass = require("gulp-sass");
const source = require("vinyl-source-stream");
const sourcemaps = require("gulp-sourcemaps");
const { eslint } = require("rollup-plugin-eslint");
const { uglify } = require("rollup-plugin-uglify");

const styleBuilds = [
  {
    app: "peerinst",
    modules: ["group", "student"],
  },
];

const scriptBuilds = [
  {
    app: "peerinst",
    modules: ["group", "student", "ajax", "search", "index"],
  },
];

const babelConfig = {
  presets: [
    [
      "@babel/env",
      {
        targets: {
          browsers: [
            "last 3 versions",
            "iOS>=8",
            "ie 11",
            "Safari 9.1",
            "not dead",
          ],
        },
        modules: false,
      },
    ],
  ],
  exclude: "node_modules/**",
  babelrc: false,
};

function buildStyle(app, module) {
  const build = gulp
    .src("./" + app + "/static/" + app + "/css/" + module + "/*.scss")
    .pipe(sourcemaps.init())
    .pipe(
      sass({
        outputStyle: "compressed",
        includePaths: "./node_modules",
      }),
    )
    .pipe(
      postcss([
        autoprefixer({
          browsers: [
            "last 3 versions",
            "iOS>=8",
            "ie 11",
            "Safari 9.1",
            "not dead",
          ],
        }),
      ]),
    )
    .pipe(concat(module + ".min.css"))
    .pipe(sourcemaps.write("."))
    .pipe(gulp.dest("./" + app + "/static/" + app + "/css"));

  return build;
}

function watchStyle(app, module) {
  gulp.watch(
    "./" + app + "/static/" + app + "/css/" + module + "/*.scss",
    () => buildStyle(app, module),
  );
}

function buildScript(app, module) {
  const name = module === "index" ? "bundle" : module;
  const build = rollup({
    input: "./" + app + "/static/" + app + "/js/" + module + ".js",
    sourcemap: true,
    format: "iife",
    name: name,
    globals: {
      flatpickr: "flatpickr", // eslint-disable-line
      // d3: "d3", // eslint-disable-line
      "@material/auto-init": "@material/auto-init",
      "@material/checkbox": "@material/checkbox",
      "@material/chips": "@material/chips",
      "@material/dialog": "@material/dialog",
      "@material/drawer": "@material/drawer",
      "@material/icon-toggle": "@material/icon-toggle",
      "@material/radio": "@material/radio",
      "@material/ripple": "@material/ripple",
      "@material/select": "@material/select",
      "@material/textfield": "@material/textfield",
      "@material/toolbar": "@material/toolbar",
    },
    plugins: [
      resolve({
        jsnext: true,
        main: true,
        browser: true,
      }),
      commonjs(),
      eslint({
        exclude: ["**.css"],
      }),
      babel(babelConfig),
      uglify(),
    ],
    external: [
      "flatpickr",
      // "d3",
      "@material/auto-init",
      "@material/checkbox",
      "@material/chips",
      "@material/dialog",
      "@material/drawer",
      "@material/icon-toggle",
      "@material/radio",
      "@material/ripple",
      "@material/select",
      "@material/textfield",
      "@material/toolbar",
    ],
  })
    .pipe(source(module + ".min.js"))
    .pipe(buffer())
    .pipe(sourcemaps.init({ loadMaps: true }))
    .pipe(sourcemaps.write("."))
    .pipe(gulp.dest("./" + app + "/static/" + app + "/js"));

  return build;
}

function watchScript(app, module) {
  gulp.watch(
    [
      "./" + app + "/static/" + app + "/js/_" + module + "/*.js",
      "./" + app + "/static/" + app + "/js/" + module + ".js",
    ],
    () => buildScript(app, module),
  );
}

function stylesPeerinstMain() {
  const build = gulp
    .src("./peerinst/static/peerinst/css/*.scss")
    .pipe(sourcemaps.init())
    .pipe(
      sass({
        outputStyle: "compressed",
        includePaths: "./node_modules",
      }),
    )
    .pipe(
      postcss([
        autoprefixer({
          browsers: [
            "last 3 versions",
            "iOS>=8",
            "ie 11",
            "Safari 9.1",
            "not dead",
          ],
        }),
      ]),
    )
    .pipe(
      rename(path => {
        path.extname = ".min.css";
      }),
    )
    .pipe(sourcemaps.write("."))
    .pipe(gulp.dest("./peerinst/static/peerinst/css/"));

  return build;
}

function stylesPeerinstPinax() {
  const build = gulp
    .src("./peerinst/static/pinax/forums/css/*.scss")
    .pipe(sourcemaps.init())
    .pipe(
      sass({
        outputStyle: "compressed",
        includePaths: "./node_modules/",
      }),
    )
    .pipe(
      rename(path => {
        path.extname = "min.css";
      }),
    )
    .pipe(sourcemaps.write("."))
    .pipe(gulp.dest("./peerinst/static/pinax/forums/css/"));

  return build;
}

function scriptsPeerinstPinax() {
  const build = merge([
    rollup({
      input: "./peerinst/static/pinax/forums/js/thread.js",
      sourcemap: true,
      format: "iife",
      name: "bundle",
      globals: {
        flatpickr: "flatpickr",
        d3: "d3",
      },
      plugins: [
        eslint({
          exclude: ["**.css"],
        }),
        babel(babelConfig),
        uglify(),
      ],
      external: ["flatpickr", "d3"],
    })
      .pipe(source("thread.min.js"))
      .pipe(buffer())
      .pipe(sourcemaps.init({ loadMaps: true }))
      .pipe(sourcemaps.write("."))
      .pipe(gulp.dest("./peerinst/static/pinax/forums/js")),
    rollup({
      input: "./peerinst/static/pinax/forums/js/limit.js",
      sourcemap: true,
      format: "iife",
      name: "bundle",
      globals: {
        flatpickr: "flatpickr",
        d3: "d3",
      },
      plugins: [
        eslint({
          exclude: ["**.css"],
        }),
        babel(babelConfig),
        uglify(),
      ],
      external: ["flatpickr", "d3"],
    })
      .pipe(source("limit.min.js"))
      .pipe(buffer())
      .pipe(sourcemaps.init({ loadMaps: true }))
      .pipe(sourcemaps.write("."))
      .pipe(gulp.dest("./peerinst/static/pinax/forums/js")),
  ]);

  return build;
}

function watch() {
  gulp.watch("./peerinst/static/peerinst/css/*.scss", stylesPeerinstMain);
  gulp.watch("./peerinst/static/pinax/forums/css/*.scss", stylesPeerinstPinax);
  styleBuilds.forEach(s => s.modules.forEach(m => watchStyle(s.app, m)));
  scriptBuilds.forEach(s => s.modules.forEach(m => watchScript(s.app, m)));
  gulp.watch(
    [
      "./peerinst/static/peerinst/js/*.js",
      "!./peerinst/static/peerinst/js/*.min.js*",
      "!./peerinst/static/peerinst/js/utils.js",
    ].concat(
      scriptBuilds
        .filter(s => s.app === "peerinst")
        .map(s => s.modules)
        .filter(m => m !== "index")
        .map(m => "./peerinst/static/peerinst/js/" + m + ".js"),
    ),
    () => buildScript("peerinst", "index"),
  );
}

const styles = gulp.parallel(
  stylesPeerinstMain,
  stylesPeerinstPinax,
  ...[].concat(
    ...styleBuilds.map(s => s.modules.map(m => () => buildStyle(s.app, m))),
  ),
);

const scripts = gulp.parallel(
  scriptsPeerinstPinax,
  ...[].concat(
    ...scriptBuilds.map(s => s.modules.map(m => () => buildScript(s.app, m))),
  ),
);

const build = gulp.parallel(styles, scripts);

exports.build = build;
exports.watch = watch;
exports.styles = styles;
exports.scripts = scripts;
