import React from 'react';
import vAlignImage from '/utils/vAlignImage';

export default function Spaceship(props) {
  return (
    <img style={{ ...props.style, ...vAlignImage }}
      src='/public/spacecat.gif'/>
  );
}
