import React from 'react';
import vAlignImage from '/utils/vAlignImage';

export default function Spaceship(props) {
  return (
    <img style={{ ...props.style, ...vAlignImage }}
      src="http://24.media.tumblr.com/8210fd413c5ce209678ef82d65731443/tumblr_mjphnqLpNy1s5jjtzo1_400.gif"/>
  );
}
