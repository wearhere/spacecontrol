/* eslint-disable no-console */
const _ = require('underscore');
const babel = require('rollup-plugin-babel');
const del = require('del');
const gulp = require('gulp');
const MultiBuild = require('multibuild');
const nodemon = require('gulp-nodemon');
const rename = require('gulp-rename');
const rootImport = require('rollup-plugin-root-import');
const runSequence = require('run-sequence');
const sourcemaps = require('gulp-sourcemaps');

const TARGETS = ['app'];

const build = new MultiBuild({
  gulp,
  targets: TARGETS,
  entry: (target) => `src/client/main-${target}.js`,
  rollupOptions: {
    external: ['jquery', 'backbone', 'underscore', 'react', 'react-dom'],
    globals: {
      jquery: '$',
      underscore: '_',
      backbone: 'Backbone',
      react: 'React',
      'react-dom': 'ReactDOM'
    },
    plugins: [
      rootImport({
        root: [`${__dirname}/src/client`],
        // Because we omit the .js most of the time, we put it first, and
        // explicitly specify that it should attempt the lack of extension
        // only after it tries to resolve with the extension.
        extensions: ['.js', '.jsx', '']
      }),
      babel({
        plugins: [
          'external-helpers',
          'syntax-jsx',
          'transform-react-jsx',
          'transform-react-display-name'
        ]
      })
    ],
    format: 'iife',
    sourcemap: true
  },
  output: (target, input) => {
    return input
      .pipe(rename(`build-${target}.js`))
      .pipe(sourcemaps.write('.'))
      .pipe(gulp.dest('public'));
  }
});

gulp.task('clean', function() {
  const js = _.flatten(TARGETS.map(target => [
    `public/build-${target}.js`,
    `public/build-${target}.js.map`,
  ]));
  return del(js);
});

gulp.task('js', ['clean'], function(cb) {
  build.runAll(cb);
});

gulp.task('watch', function() {
  gulp.watch('src/client/**/*.js', (file) => build.changed(file.path));
});

gulp.task('server', function() {
  nodemon({
    script: 'src/server/app.js',
    ext: 'js',
    watch: ['src/server/**/*']
  });
});

gulp.task('default', function(cb) {
  runSequence('js', ['watch', 'server'], cb);
});
