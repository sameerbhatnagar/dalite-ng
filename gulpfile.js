const autoprefixer = require("autoprefixer");
// const replace = require("gulp-replace");
// const fs = require("fs");
const concat = require("gulp-concat");
// const crypto = require("crypto");
const cssnano = require("cssnano");
const gulp = require("gulp");
// const merge = require("merge-stream");
const postcss = require("gulp-postcss");
const rename = require("gulp-rename");
const runSequence = require("run-sequence");
const sass = require("gulp-sass");
const sourcemaps = require("gulp-sourcemaps");

// const hash = path =>
// new Promise((resolve, reject) => {
// fs.createReadStream(path)
// .on("error", reject)
// .pipe(crypto.createHash("sha1").setEncoding("hex"))
// .once("finish", function() {
// resolve(this.read()); // eslint-disable-line no-invalid-this
// });
// });

// Run sass and minify
gulp.task("sass", function() {
  return gulp
    .src("./peerinst/static/peerinst/css/*.scss")
    .pipe(
      rename(function(path) {
        path.extname = ".min.css";
      }),
    )
    .pipe(sourcemaps.init())
    .pipe(
      sass({
        outputStyle: "compressed",
        includePaths: "./node_modules/",
      }),
    )
    .pipe(sourcemaps.write("."))
    .pipe(gulp.dest("./peerinst/static/peerinst/css/"));
});

gulp.task("pinax-sass", function() {
  return gulp
    .src("./peerinst/static/pinax/forums/css/*.scss")
    .pipe(
      rename(function(path) {
        path.extname = ".min.css";
      }),
    )
    .pipe(sourcemaps.init())
    .pipe(
      sass({
        outputStyle: "compressed",
        includePaths: "./node_modules/",
      }),
    )
    .pipe(sourcemaps.write("."))
    .pipe(gulp.dest("./peerinst/static/pinax/forums/css/"));
});

// Process native css files not minified already
gulp.task("css", function() {
  return gulp
    .src([
      "./peerinst/static/peerinst/css/*.css",
      "!./peerinst/static/peerinst/css/*.min.css",
    ])
    .pipe(
      rename(function(path) {
        path.extname = ".min.css";
      }),
    )
    .pipe(postcss([cssnano()]))
    .pipe(gulp.dest("./peerinst/static/peerinst/css/"));
});

// Run autoprefixer on minified css files
gulp.task("autoprefixer", function() {
  return gulp
    .src("./peerinst/static/peerinst/css/*.min.css")
    .pipe(sourcemaps.init())
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
    .pipe(sourcemaps.write("."))
    .pipe(gulp.dest("./peerinst/static/peerinst/css/"));
});

gulp.task("peerinst-styles", function(callback) {
  runSequence("sass", "pinax-sass", "css", "autoprefixer", callback);
});

gulp.task("peerinst-styles-group", function() {
  const app = "peerinst";
  const module = "group";

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
    .pipe(gulp.dest(app + "/static/" + app + "/css"));

  return build;
});

gulp.task("peerinst-styles-student", async function() {
  const app = "peerinst";
  const module = "student";
  // const templates = ["student/base.html"];

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
    .pipe(gulp.dest(app + "/static/" + app + "/css"));

  // const hash_ = await hash(
  // "./" + app + "/static/" + app + "/css" + module + ".min.css",
  // );
  //
  // const updateHash = gulp
  // .src("./" + app + "/templates/" + app + "/" + templatePath)
  // .pipe(
  // replace(
  // new RegExp(
  // "({%\\s*static 'peerinst\\/css\\/" +
  // filename +
  // "'\\s*%})(?:\\?hash=.{8})?",
  // ),
  // "$1?hash=" + hash_.slice(0, 8),
  // ),
  // )
  // .pipe(gulp.dest("./peerinst/templates/peerinst/student"));
  //
  // return merge(build, updateHash);
  return build;
});

gulp.task("peerinst-scripts-index", function() {
  const runCommand = require("child_process").execSync;
  runCommand(
    "./node_modules/.bin/rollup -c ./rollup/peerinst/index-rollup.config.js",
    function(err, stdout, stderr) {
      console.log("Output: " + stdout);
      console.log("Error: " + stderr);
      if (err) {
        console.log("Error: " + err);
      }
    },
  );
});

gulp.task("peerinst-scripts-group", function() {
  const runCommand = require("child_process").execSync;
  runCommand(
    "./node_modules/.bin/rollup -c ./rollup/peerinst/group-rollup.config.js",
    function(err, stdout, stderr) {
      console.log("Output: " + stdout);
      console.log("Error: " + stderr);
      if (err) {
        console.log("Error: " + err);
      }
    },
  );
});

gulp.task("peerinst-scripts-student", async function() {
  // const app = "peerinst";
  // const filename = "student.min.js";
  // const templatePath = "student/base.html";

  const runCommand = require("child_process").execSync;
  runCommand(
    "./node_modules/.bin/rollup -c ./rollup/peerinst/student-rollup.config.js",
    function(err, stdout, stderr) {
      console.log("Output: " + stdout);
      console.log("Error: " + stderr);
      if (err) {
        console.log("Error: " + err);
      }
    },
  );

  // const hash_ = await hash(
  // "./" + app + "/templates/" + app + "/" + templatePath,
  // );
  //
  // return gulp
  // .src("./" + app + "/templates/" + app + "/" + templatePath)
  // .pipe(
  // replace(
  // new RegExp(
  // "({%\\s*static 'peerinst\\/js\\/" +
  // filename +
  // "'\\s*%})(?:\\?hash=.{8})?",
  // ),
  // "$1?hash=" + hash_.slice(0, 8),
  // ),
  // )
  // .pipe(gulp.dest("./peerinst/templates/peerinst/student"));
});

gulp.task("peerinst-scripts-ajax", function() {
  const runCommand = require("child_process").execSync;
  runCommand(
    "./node_modules/.bin/rollup -c ./rollup/peerinst/ajax-rollup.config.js",
    function(err, stdout, stderr) {
      console.log("Output: " + stdout);
      console.log("Error: " + stderr);
      if (err) {
        console.log("Error: " + err);
      }
    },
  );
});

gulp.task("peerinst-scripts-search", function() {
  const runCommand = require("child_process").execSync;
  runCommand(
    "./node_modules/.bin/rollup -c ./rollup/peerinst/search-rollup.config.js",
    function(err, stdout, stderr) {
      console.log("Output: " + stdout);
      console.log("Error: " + stderr);
      if (err) {
        console.log("Error: " + err);
      }
    },
  );
});

gulp.task("pinax-forums-scripts-forums", function() {
  const runCommand = require("child_process").execSync;
  runCommand(
    "./node_modules/.bin/rollup -c ./rollup/peerinst/pinax/forums/forums-rollup.config.js", // eslint-disable-line max-len
    function(err, stdout, stderr) {
      console.log("Output: " + stdout);
      console.log("Error: " + stderr);
      if (err) {
        console.log("Error: " + err);
      }
    },
  );
});


gulp.task("peerinst-scripts", function(callback) {
  runSequence(
    "peerinst-scripts-index",
    "peerinst-scripts-group",
    "peerinst-scripts-student",
    "peerinst-scripts-ajax",
    "peerinst-scripts-search",
    "pinax-forums-scripts-forums",
    callback,
  );
});

gulp.task("peerinst-build", function(callback) {
  runSequence(
    "peerinst-styles",
    "peerinst-styles-group",
    "peerinst-styles-student",
    "peerinst-scripts",
    callback,
  );
});

gulp.task("tos-styles", function() {
  return gulp
    .src("./tos/static/tos/css/*.scss")
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
    .pipe(concat("styles.min.css"))
    .pipe(sourcemaps.write("."))
    .pipe(gulp.dest("tos/static/tos/css"));
});

gulp.task("tos-scripts-tos", function() {
  const runCommand = require("child_process").execSync;
  runCommand(
    "./node_modules/.bin/rollup -c ./rollup/tos/tos-rollup.config.js",
    function(err, stdout, stderr) {
      console.log("Output: " + stdout);
      console.log("Error: " + stderr);
      if (err) {
        console.log("Error: " + err);
      }
    },
  );
});

gulp.task("tos-scripts-email", function() {
  const runCommand = require("child_process").execSync;
  runCommand(
    "./node_modules/.bin/rollup -c ./rollup/tos/email-rollup.config.js",
    function(err, stdout, stderr) {
      console.log("Output: " + stdout);
      console.log("Error: " + stderr);
      if (err) {
        console.log("Error: " + err);
      }
    },
  );
});

gulp.task("tos-scripts", function(callback) {
  runSequence("tos-scripts-tos", "tos-scripts-email", callback);
});

gulp.task("tos-build", function(callback) {
  runSequence("tos-styles", "tos-scripts", callback);
});

gulp.task("build", function(callback) {
  runSequence("peerinst-build", "tos-build", callback);
});

gulp.task("watch", function() {
  gulp.watch("./tos/static/tos/css/*.scss", ["tos-styles"]);
  gulp.watch("./tos/static/tos/js/tos.js", ["tos-scripts-tos"]);
  gulp.watch("./tos/static/tos/js/email.js", ["tos-scripts-email"]);
  gulp.watch("./peerinst/static/peerinst/css/*.scss", ["peerinst-styles"]);
  gulp.watch("./peerinst/static/peerinst/css/group/*.scss", [
    "peerinst-styles-group",
  ]);
  gulp.watch("./peerinst/static/peerinst/css/student/*.scss", [
    "peerinst-styles-student",
  ]);
  gulp.watch(
    [
      "./peerinst/static/peerinst/js/*.js",
      "!./peerinst/static/peerinst/js/group.js",
      "!./peerinst/static/peerinst/js/student.js",
      "!./peerinst/static/peerinst/js/*.min.js",
      "!./peerinst/static/peerinst/js/utils.js",
    ],
    ["peerinst-scripts-index"],
  );
  gulp.watch(
    [
      "./peerinst/static/peerinst/js/_group/*.js",
      "./peerinst/static/peerinst/js/group.js",
    ],
    ["peerinst-scripts-group"],
  );
  gulp.watch(
    [
      "./peerinst/static/peerinst/js/_student/*.js",
      "./peerinst/static/peerinst/js/student.js",
    ],
    ["peerinst-scripts-student"],
  );
  gulp.watch(
    [
      "./peerinst/static/peerinst/js/_ajax/*.js",
      "./peerinst/static/peerinst/js/ajax.js",
    ],
    ["peerinst-scripts-ajax", "peerinst-scripts-group"],
  );
});
