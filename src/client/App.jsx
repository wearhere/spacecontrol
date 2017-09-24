import CBR from 'connect-backbone-to-react';
const { connectBackboneToReact } = CBR;
import React from 'react';

function App(props) {
  return <img style={{marginLeft: `${props.progress}px`}} src="http://24.media.tumblr.com/8210fd413c5ce209678ef82d65731443/tumblr_mjphnqLpNy1s5jjtzo1_400.gif"/>;
}

function mapModelsToProps({ model }) {
  return {
    progress: model.get('progress')
  };
}

export default connectBackboneToReact(mapModelsToProps)(App);
