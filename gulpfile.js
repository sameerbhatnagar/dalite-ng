const gulp = require('gulp');
const rename = require('gulp-rename');
const sass = require('gulp-sass');
const sourcemaps = require('gulp-sourcemaps');
const postcss = require('gulp-postcss');
const cssnano = require('cssnano');
const autoprefixer = require('autoprefixer');
const runSequence = require('run-sequence');
// const rollup = require('rollup-stream');
// const source = require('vinyl-source-stream');

// Run sass and minify
gulp.task('sass', function() {
  return gulp.src('./peerinst/static/peerinst/css/*.scss')
    .pipe(rename(function(path) {
      path.extname = '.min.css';
      }))
    .pipe(sourcemaps.init())
    .pipe(sass({
        outputStyle: 'compressed',
        includePaths: './node_modules/',
      }))
    .pipe(sourcemaps.write('.'))
    .pipe(gulp.dest('./peerinst/static/peerinst/css/'));
});

// Process native css files not minified already
gulp.task('css', function() {
    return gulp.src(['./peerinst/static/peerinst/css/*.css',
                     '!./peerinst/static/peerinst/css/*.min.css'])
      .pipe(rename(function(path) {
        path.extname = '.min.css';
        }))
      .pipe(postcss([cssnano()]))
      .pipe(gulp.dest('./peerinst/static/peerinst/css/'));
});

// Run autoprefixer on minified css files
gulp.task('autoprefixer', function() {
    return gulp.src('./peerinst/static/peerinst/css/*.min.css')
        .pipe(sourcemaps.init())
        .pipe(postcss([autoprefixer({
          browsers:
            ['last 3 versions', 'iOS>=8', 'ie 11', 'Safari 9.1', 'not dead'],
         })]))
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
    console.log('Output: '+stdout);
    console.log('Error: '+stderr);
    if (err) {
      console.log('Error: '+err);
    }
  });
});

gulp.task('build', function(callback) {
     runSequence('sass', 'css', 'autoprefixer', 'rollup', callback);
});
