/* eslint-disable no-console */
const _ = require('underscore');
const babel = require('rollup-plugin-babel');
const cache = require('gulp-cached');
const commonJS = require('rollup-plugin-commonjs');
const del = require('del');
const gulp = require('gulp');
const MultiBuild = require('multibuild');
const livereload = require('gulp-livereload');
const nodemon = require('gulp-nodemon');
const nodeResolve = require('rollup-plugin-node-resolve');
const rename = require('gulp-rename');
const replace = require('rollup-plugin-replace');
const rootImport = require('rollup-plugin-root-import');
const runSequence = require('run-sequence');
const sourcemaps = require('gulp-sourcemaps');
const watch = require('gulp-watch');

const TARGETS = ['app'];

const build = new MultiBuild({
  gulp,
  targets: TARGETS,
  entry: (target) => `src/client/main-${target}.jsx`,
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
      /**
       * Specify environment for React per
       * https://facebook.github.io/react/docs/optimizing-performance.html#rollup and
       * https://github.com/rollup/rollup/issues/487#issuecomment-177596512.
       */
      replace({
        'process.env.NODE_ENV': '"development"'
      }),
      rootImport({
        root: [`${__dirname}/src/client`],
        // Because we omit the .js most of the time, we put it first, and
        // explicitly specify that it should attempt the lack of extension
        // only after it tries to resolve with the extension.
        extensions: ['.js', '.jsx', '']
      }),
      nodeResolve(),
      commonJS({
        include: 'node_modules/**',
      }),
      babel({
        plugins: [
          'external-helpers',
          'syntax-jsx',
          'transform-react-jsx',
          'transform-react-display-name'
        ],
        exclude: 'node_modules/**'
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
  livereload.listen({
    port: 22222
  });

  // JS and JSX.
  watch('src/client/**/*', (file) => build.changed(file.path));

  watch('public/**')
    .pipe(cache('buildCache', { optimizeMemory: true })
      .on('data', function(file) {
        livereload.changed(file.path);
      }));
});

gulp.task('server', function() {
  nodemon({
    script: 'src/server/app.js',
    ext: 'js, html',
    watch: ['src/server/**/*']
  })
    .on('restart', function() {
      // Workaround: https://github.com/JacksonGariety/gulp-nodemon/issues/40
      // Wait for server to finish loading.
      setTimeout(function() {
        livereload.reload();
      }, 1000);
    });
});

gulp.task('default', function(cb) {
  runSequence('js', ['watch', 'server'], cb);
});
