import { ActivityIndicator, View, StyleSheet } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { useAuth } from '../context/AuthContext';
import AuthStack from './AuthStack';
import CitoyenNavigator from './CitoyenNavigator';
import CamioneurNavigator from './CamioneurNavigator';
import colors from '../theme/colors';

export default function RootNavigator() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <View style={styles.loader}>
        <ActivityIndicator size="large" color={colors.primary} />
      </View>
    );
  }

  let tree = <AuthStack />;
  if (user?.role === 'citoyen') tree = <CitoyenNavigator />;
  else if (user?.role === 'camioneur') tree = <CamioneurNavigator />;

  return (
    <NavigationContainer>
      {tree}
    </NavigationContainer>
  );
}

const styles = StyleSheet.create({
  loader: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.background,
  },
});
