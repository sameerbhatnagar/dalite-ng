const gulp = require('gulp');
const rename = require('gulp-rename');
const sass = require('gulp-sass');
const sourcemaps = require('gulp-sourcemaps');
const postcss = require('gulp-postcss');
const cssnano = require('cssnano');
const autoprefixer = require('autoprefixer');
const runSequence = require('run-sequence');
const concat = require('gulp-concat');
// const rollup = require('rollup-stream');
// const source = require('vinyl-source-stream');

// Run sass and minify
gulp.task('sass', function() {
  return gulp
    .src('./peerinst/static/peerinst/css/*.scss')
    .pipe(
      rename(function(path) {
        path.extname = '.min.css';
      }),
    )
    .pipe(sourcemaps.init())
    .pipe(
      sass({
        outputStyle: 'compressed',
        includePaths: './node_modules/',
      }),
    )
    .pipe(sourcemaps.write('.'))
    .pipe(gulp.dest('./peerinst/static/peerinst/css/'));
});

// Process native css files not minified already
gulp.task('css', function() {
  return gulp
    .src([
      './peerinst/static/peerinst/css/*.css',
      '!./peerinst/static/peerinst/css/*.min.css',
    ])
    .pipe(
      rename(function(path) {
        path.extname = '.min.css';
      }),
    )
    .pipe(postcss([cssnano()]))
    .pipe(gulp.dest('./peerinst/static/peerinst/css/'));
});

// Run autoprefixer on minified css files
gulp.task('autoprefixer', function() {
  return gulp
    .src('./peerinst/static/peerinst/css/*.min.css')
    .pipe(sourcemaps.init())
    .pipe(
      postcss([
        autoprefixer({
          browsers: [
            'last 3 versions',
            'iOS>=8',
            'ie 11',
            'Safari 9.1',
            'not dead',
          ],
        }),
      ]),
    )
    .pipe(sourcemaps.write('.'))
    .pipe(gulp.dest('./peerinst/static/peerinst/css/'));
});

/* Not working; error thrown
gulp.task('rollup', function() {
  return rollup('rollup.config.js')
    .pipe(source('index.min.js'))
    .pipe(gulp.dest('./peerinst/static/peerinst/js/'));
});*/

gulp.task('peerinst-styles', function(callback) {
  runSequence('sass', 'css', 'autoprefixer', callback);
});

gulp.task('peerinst-styles-group', function() {
  return gulp
    .src('./peerinst/static/peerinst/css/group/*.scss')
    .pipe(sourcemaps.init())
    .pipe(
      sass({
        outputStyle: 'compressed',
        includePaths: './node_modules',
      }),
    )
    .pipe(
      postcss([
        autoprefixer({
          browsers: [
            'last 3 versions',
            'iOS>=8',
            'ie 11',
            'Safari 9.1',
            'not dead',
          ],
        }),
      ]),
    )
    .pipe(
      rename(function(path) {
        path.dirname += '/group';
        path.extname = '.min.css';
      }),
    )
    .pipe(sourcemaps.write('.'))
    .pipe(gulp.dest('peerinst/static/peerinst/css'));
});

gulp.task('peerinst-scripts-index', function() {
  const runCommand = require('child_process').execSync;
  runCommand(
    './node_modules/.bin/rollup -c ./rollup/peerinst/index-rollup.config.js',
    function(err, stdout, stderr) {
      console.log('Output: ' + stdout);
      console.log('Error: ' + stderr);
      if (err) {
        console.log('Error: ' + err);
      }
    },
  );
});

gulp.task('peerinst-scripts-group', function() {
  const runCommand = require('child_process').execSync;
  runCommand(
    './node_modules/.bin/rollup -c ./rollup/peerinst/group-rollup.config.js',
    function(err, stdout, stderr) {
      console.log('Output: ' + stdout);
      console.log('Error: ' + stderr);
      if (err) {
        console.log('Error: ' + err);
      }
    },
  );
});

gulp.task('peerinst-scripts', function(callback) {
  runSequence('peerinst-scripts-index', 'peerinst-scripts-index', callback);
});

gulp.task('peerinst-build', function(callback) {
  runSequence('peerinst-styles', 'peerinst-scripts', callback);
});

gulp.task('tos-styles', function() {
  return gulp
    .src('./tos/static/tos/css/*.scss')
    .pipe(sourcemaps.init())
    .pipe(
      sass({
        outputStyle: 'compressed',
        includePaths: './node_modules',
      }),
    )
    .pipe(
      postcss([
        autoprefixer({
          browsers: [
            'last 3 versions',
            'iOS>=8',
            'ie 11',
            'Safari 9.1',
            'not dead',
          ],
        }),
      ]),
    )
    .pipe(concat('styles.min.css'))
    .pipe(sourcemaps.write('.'))
    .pipe(gulp.dest('tos/static/tos/css'));
});

gulp.task('tos-scripts-tos', function() {
  const runCommand = require('child_process').execSync;
  runCommand(
    './node_modules/.bin/rollup -c ./rollup/tos/tos-rollup.config.js',
    function(err, stdout, stderr) {
      console.log('Output: ' + stdout);
      console.log('Error: ' + stderr);
      if (err) {
        console.log('Error: ' + err);
      }
    },
  );
});

gulp.task('tos-scripts-email', function() {
  const runCommand = require('child_process').execSync;
  runCommand(
    './node_modules/.bin/rollup -c ./rollup/tos/email-rollup.config.js',
    function(err, stdout, stderr) {
      console.log('Output: ' + stdout);
      console.log('Error: ' + stderr);
      if (err) {
        console.log('Error: ' + err);
      }
    },
  );
});

gulp.task('tos-scripts', function(callback) {
  runSequence('tos-scripts-tos', 'tos-scripts-email', callback);
});

gulp.task('tos-build', function(callback) {
  runSequence('tos-styles', 'tos-scripts', callback);
});

gulp.task('build', function(callback) {
  runSequence('peerinst-build', 'tos-build', callback);
});

gulp.task('watch', function() {
  gulp.watch('./tos/static/tos/css/*.scss', ['tos-styles']);
  gulp.watch('./tos/static/tos/js/tos.js', ['tos-scripts-tos']);
  gulp.watch('./tos/static/tos/js/email.js', ['tos-scripts-email']);
  // gulp.watch('./peerinst/static/peerinst/css/**/*.scss', ['peerinst-styles']);
  gulp.watch('./peerinst/static/peerinst/css/group/*.scss', [
    'peerinst-styles-group',
  ]);
  gulp.watch(
    [
      './peerinst/static/peerinst/js/_group/*.js',
      './peerinst/static/peerinst/js/group.js',
    ],
    ['tos-scripts-group'],
  );
});
