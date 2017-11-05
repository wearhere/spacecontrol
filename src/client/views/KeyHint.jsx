import React from 'react';
import ReactTestUtils from 'react-dom/test-utils';
import Status from '/views/Status';

export default class KeyHint extends React.Component {
  trigger() {
    if (!document.activeElement) return;

    // HACK(jeff): We can assume that body events are listened to with jQuery. Otherwise we need
    // to trigger React's system.
    if (document.activeElement === document.body) {
      document.body.dispatchEvent(new KeyboardEvent('keydown', {
        key: this.props.triggerKey
      }));
    } else {
      ReactTestUtils.Simulate.keyDown(document.activeElement, {
        key: this.props.triggerKey
      });
    }
  }

  render() {
    return <Status>{this.props.children}</Status>;
  }
}
