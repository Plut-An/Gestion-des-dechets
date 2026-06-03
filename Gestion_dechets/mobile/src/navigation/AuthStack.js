import { createNativeStackNavigator } from '@react-navigation/native-stack';
import WelcomeScreen from '../screens/auth/WelcomeScreen';
import LoginScreen from '../screens/auth/LoginScreen';
import RegisterCitoyenScreen from '../screens/auth/RegisterCitoyenScreen';
import RegisterCamioneurScreen from '../screens/auth/RegisterCamioneurScreen';
import colors from '../theme/colors';

const Stack = createNativeStackNavigator();

export default function AuthStack() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
        contentStyle: { backgroundColor: colors.background },
      }}
    >
      <Stack.Screen name="Welcome" component={WelcomeScreen} />
      <Stack.Screen name="Login" component={LoginScreen} />
      <Stack.Screen name="RegisterCitoyen" component={RegisterCitoyenScreen} />
      <Stack.Screen name="RegisterCamioneur" component={RegisterCamioneurScreen} />
    </Stack.Navigator>
  );
}
