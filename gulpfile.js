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

// Run rollup to bundle js
gulp.task('rollup', function() {
  const runCommand = require('child_process').execSync;
  runCommand('./node_modules/.bin/rollup -c', function(err, stdout, stderr) {
    console.log('Output: ' + stdout);
    console.log('Error: ' + stderr);
    if (err) {
      console.log('Error: ' + err);
    }
  });
});

gulp.task('build', function(callback) {
  runSequence('sass', 'css', 'autoprefixer', 'rollup', callback);
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

gulp.task('tos-build', function(callback) {
  runSequence('tos-styles', 'tos-scripts-tos', 'tos-scripts-email', callback);
});

gulp.task('watch', function() {
  gulp.watch('./tos/static/tos/css/*.scss', ['tos-styles']);
  gulp.watch('./tos/static/tos/js/tos.js', ['tos-scripts-tos']);
  gulp.watch('./tos/static/tos/js/email.js', ['tos-scripts-email']);
});
