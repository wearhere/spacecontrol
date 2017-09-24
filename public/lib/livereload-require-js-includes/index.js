/* eslint browser: true */
(function() {
  'use strict';

  // This was modeled after the Less plugin bundled with livereload:
  // https://github.com/livereload/livereload-js/blob/e1d943628005ad8d18a50ee1e8c29858ca748d10/dist/livereload.js#L219
  function RequireJSIncludes(window) {
    /* jshint unused:vars */
    this.window = window;
  }

  RequireJSIncludes.identifier = 'com.mixmax.livereloadplugin.requirejsincludes';

  RequireJSIncludes.version = '1.0';

  RequireJSIncludes.prototype.reload = function(path) {
    /* jshint unused:vars */

    // The filename is the last path component.
    // TODO(jeff): This probably doesn't support Windows…?
    var filename = path.split('/').slice(-1)[0];

    // Note that we'll never reload for sourcemaps since we capture them here and they're not
    // included on the page.
    var fileIsJS = /\.(?:js|map)$/.test(filename);
    if (!fileIsJS) {
      // Let LiveReload handle this file.
      return false;
    }

    var fileIsRelevant = !!document.querySelector('script[src$="' + filename +'"]');
    if (fileIsRelevant) {
      // This is how LiveReload reloads.
      this.window.document.location.reload();
    }

    // Never let LiveReload handle JS--we either reloaded above or the script wasn't relevant.
    return true;
  };

  if (window.LiveReload) {
    window.LiveReload.addPlugin(RequireJSIncludes);
  } else {
    // LiveReload automatically loads objects beginning with "LiveReloadPlugin" when it loads.
    window.LiveReloadPlugin_RequireJSIncludes = RequireJSIncludes;
  }
})();
