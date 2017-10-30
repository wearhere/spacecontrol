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

const TARGETS = [
  'app',
  'keyboardPanel'
];

const build = new MultiBuild({
  gulp,
  targets: TARGETS,
  entry: (target) => {
    if (target === 'keyboardPanel') {
      return 'panels/keyboardPanel.jsx';
    } else {
      return `src/client/main-${target}.jsx`;
    }
  },
  rollupOptions: (target) => {
    if (target === 'keyboardPanel') {
      return {
        plugins: [
          babel({
            plugins: [
              ['transform-react-jsx', { pragma: 'h' }],
              'babel-plugin-transform-function-bind'
            ],
            exclude: 'node_modules/**'
          })
        ],
        format: 'cjs'
      };
    } else {
      return {
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
            root: [`${__dirname}/src/client`, `${__dirname}/src/common`],
            // Because we omit the .js most of the time, we put it first, and
            // explicitly specify that it should attempt the lack of extension
            // only after it tries to resolve with the extension.
            extensions: ['.js', '.jsx', '']
          }),
          nodeResolve(),
          commonJS({
            include: ['node_modules/**', 'src/common/**'],
            namedExports: {
              'src/common/GameConstants.js': [
                'GAME_STATE',
                'SUN_INITIAL_PROGRESS',
                'SUN_PROGRESS_INCREMENT',
                'SUN_UPDATE_INTERVAL_MS',
                'DANGER_DISTANCE'
              ]
            }
          }),
          babel({
            // Don't transpile to ES5, we can assume this will only run in modern browsers.
            plugins: [
              'external-helpers',
              'syntax-jsx',
              'transform-react-jsx',
              'transform-react-display-name',
              'transform-object-rest-spread'
            ],
            exclude: 'node_modules/**'
          })
        ],
        format: 'iife',
        sourceMap: true
      };
    }
  },
  output: (target, input) => {
    if (target === 'keyboardPanel') {
      return input
        .pipe(rename('keyboardPanel.js'))
        .pipe(gulp.dest('panels'));
    } else {
      return input
        .pipe(rename(`build-${target}.js`))
        .pipe(sourcemaps.write('.'))
        .pipe(gulp.dest('public'));
    }
  }
});

gulp.task('clean', function() {
  const js = _.flatten(TARGETS.map(target => {
    if (target === 'keyboardPanel') {
      return 'panels/keyboardPanel.js';
    } else {
      return [
        `public/build-${target}.js`,
        `public/build-${target}.js.map`,
      ];
    }
  }));
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
  watch(['src/client/**/*', 'panels/keyboardPanel.jsx'], (file) => build.changed(file.path));

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
    watch: ['src/server/**/*', 'src/common/**/*']
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
