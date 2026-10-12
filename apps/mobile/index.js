import { registerRootComponent } from 'expo';

import App from './App';
import { TimersProvider } from './hooks/useTimers';

const Root = () => (
  <TimersProvider>
    <App />
  </TimersProvider>
);

// registerRootComponent calls AppRegistry.registerComponent('main', () => Root);
// It also ensures that whether you load the app in Expo Go or in a native build,
// the environment is set up appropriately
registerRootComponent(Root);
