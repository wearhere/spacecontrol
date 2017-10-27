import React from 'react';
import vAlignImage from '/utils/vAlignImage';

export default function Sun() {
  return <img style={{
    // Make the sun overwhelming.
    // HACK(jeff): The positioning numbers in `App` depend on this value.
    height: '200vh',
    ...vAlignImage
  }} src="/public/sun.png"/>;
}
