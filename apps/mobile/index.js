import { registerRootComponent } from 'expo';
import { SafeAreaProvider } from 'react-native-safe-area-context';

import App from './App';
import { TimersProvider } from './hooks/useTimers';

const Root = () => (
  <SafeAreaProvider>
    <TimersProvider>
      <App />
    </TimersProvider>
  </SafeAreaProvider>
);

// registerRootComponent calls AppRegistry.registerComponent('main', () => Root);
// It also ensures that whether you load the app in Expo Go or in a native build,
// the environment is set up appropriately
registerRootComponent(Root);
