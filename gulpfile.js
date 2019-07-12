const autoprefixer = require("autoprefixer");
const babel = require("rollup-plugin-babel");
const browserSync = require("browser-sync").create();
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
const svgSprite = require("gulp-svg-sprite");
const { eslint } = require("rollup-plugin-eslint");
const { uglify } = require("rollup-plugin-uglify");

const styleBuilds = [
  {
    app: "peerinst",
    modules: ["group", "student", "question"],
  },
  {
    app: "tos",
    modules: ["styles"],
  },
  {
    app: "quality",
    modules: ["edit"],
  },
];

const scriptBuilds = [
  {
    app: "peerinst",
    modules: [
      "group",
      "student",
      "ajax",
      "search",
      "index",
      "question",
      "teacher",
    ],
  },
  {
    app: "tos",
    modules: ["tos", "email"],
  },
  {
    app: "quality",
    modules: ["edit"],
  },
];

const babelConfig = {
  presets: [
    "@babel/preset-flow",
    [
      "@babel/env",
      {
        modules: false,
      },
    ],
  ],
  plugins: [
    "@babel/plugin-proposal-optional-chaining",
    [
      "@babel/plugin-transform-runtime",
      {
        helpers: false,
        regenerator: true,
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
    .pipe(postcss([autoprefixer()]))
    .pipe(concat(module + ".min.css"))
    .pipe(sourcemaps.write("."))
    .pipe(gulp.dest("./" + app + "/static/" + app + "/css"))
    .pipe(browserSync.stream());

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
      "@babel/runtime": "@babel/runtime",
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
    external: [
      "flatpickr",
      "@babel/runtime",
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
    plugins: [
      eslint({
        exclude: ["**.css"],
      }),
      babel(babelConfig),
      resolve({
        mainFields: ["module", "main", "browser"],
      }),
      commonjs(),
      uglify(),
    ],
  })
    .pipe(source(module + ".min.js"))
    .pipe(buffer())
    .pipe(sourcemaps.init({ loadMaps: true }))
    .pipe(sourcemaps.write("."))
    .pipe(gulp.dest("./" + app + "/static/" + app + "/js"))
    .pipe(browserSync.stream());

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
    .pipe(postcss([autoprefixer()]))
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
        path.extname = ".min.css";
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
      name: "thread",
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
      name: "limit",
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

function icons() {
  return gulp
    .src("./peerinst/static/peerinst/icons/*.svg")
    .pipe(
      svgSprite({
        mode: {
          symbol: {
            inline: true,
          },
        },
        svg: {
          namespaceIDs: false,
        },
      }),
    )
    .pipe(rename("icons.svg"))
    .pipe(gulp.dest("./peerinst/static/peerinst/"));
}

function watch() {
  browserSync.init({
    port: 8000,
    proxy: "localhost:8000",
    notify: false,
    open: false,
  });
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
  gulp.watch("./peerinst/static/peerinst/icons/*.svg", icons);
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

const build = gulp.parallel(styles, scripts, icons);

exports.build = build;
exports.watch = watch;
exports.styles = styles;
exports.scripts = scripts;
exports.icons = icons;
