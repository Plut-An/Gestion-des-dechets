import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import HomeScreen from '../screens/citoyen/HomeScreen';
import SignalementsScreen from '../screens/citoyen/SignalementsScreen';
import CreateSignalementScreen from '../screens/citoyen/CreateSignalementScreen';
import AssociationsScreen from '../screens/citoyen/AssociationsScreen';
import EvenementsScreen from '../screens/citoyen/EvenementsScreen';
import EvenementDetailScreen from '../screens/citoyen/EvenementDetailScreen';
import AnnoncesScreen from '../screens/citoyen/AnnoncesScreen';
import ProfilScreen from '../screens/citoyen/ProfilScreen';
import colors from '../theme/colors';
import { Ionicons } from '@expo/vector-icons';

const Tab = createBottomTabNavigator();
const Stack = createNativeStackNavigator();

function SignalementsStack() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false, contentStyle: { backgroundColor: colors.background } }}>
      <Stack.Screen name="SignalementsList" component={SignalementsScreen} />
      <Stack.Screen name="CreateSignalement" component={CreateSignalementScreen} />
    </Stack.Navigator>
  );
}

function HomeStack() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false, contentStyle: { backgroundColor: colors.background } }}>
      <Stack.Screen name="HomeMain" component={HomeScreen} />
      <Stack.Screen name="Annonces" component={AnnoncesScreen} />
    </Stack.Navigator>
  );
}

function EvenementsStack() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false, contentStyle: { backgroundColor: colors.background } }}>
      <Stack.Screen name="EvenementsList" component={EvenementsScreen} />
      <Stack.Screen name="EvenementDetail" component={EvenementDetailScreen} />
    </Stack.Navigator>
  );
}

function CitoyenTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarStyle: {
          backgroundColor: colors.surface,
          borderTopColor: colors.border,
          height: 60,
          paddingBottom: 8,
          paddingTop: 8,
        },
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.textMuted,
        tabBarIcon: ({ focused, color, size }) => {
          let iconName;
          if (route.name === 'Accueil') {
            iconName = focused ? 'home' : 'home-outline';
          } else if (route.name === 'Signalements') {
            iconName = focused ? 'trash' : 'trash-outline';
          } else if (route.name === 'Associations') {
            iconName = focused ? 'business' : 'business-outline';
          } else if (route.name === 'Evenements') {
            iconName = focused ? 'calendar' : 'calendar-outline';
          } else if (route.name === 'Profil') {
            iconName = focused ? 'person' : 'person-outline';
          }
          return <Ionicons name={iconName} size={size} color={color} />;
        },
      })}
    >
      <Tab.Screen name="Accueil" component={HomeStack} options={{ tabBarLabel: 'Accueil' }} />
      <Tab.Screen name="Signalements" component={SignalementsStack} options={{ tabBarLabel: 'Signalements' }} />
      <Tab.Screen name="Associations" component={AssociationsScreen} />
      <Tab.Screen name="Evenements" component={EvenementsStack} options={{ tabBarLabel: 'Événements' }} />
      <Tab.Screen name="Profil" component={ProfilScreen} />
    </Tab.Navigator>
  );
}

export default function CitoyenNavigator() {
  return <CitoyenTabs />;
}
