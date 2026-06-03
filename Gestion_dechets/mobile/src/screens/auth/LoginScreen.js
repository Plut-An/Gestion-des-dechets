import { useState } from 'react';
import { Alert, StyleSheet, View, ImageBackground, KeyboardAvoidingView, Platform, Text } from 'react-native';
import Screen from '../../components/Screen';
import Input from '../../components/Input';
import Button from '../../components/Button';
import Card from '../../components/Card';
import { useAuth } from '../../context/AuthContext';
import { getErrorMessage } from '../../utils/helpers';
import colors from '../../theme/colors';

export default function LoginScreen({ navigation }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const { login, logout } = useAuth();

  const handleLogin = async () => {
    if (!email || !password) {
      Alert.alert('Erreur', 'Email et mot de passe requis.');
      return;
    }
    setLoading(true);
    try {
      const user = await login(email.trim(), password);
      if (user.role !== 'citoyen' && user.role !== 'camioneur') {
        await logout();
        Alert.alert(
          'Accès mobile',
          'Cette application est réservée aux citoyens et camioneurs. Utilisez le portail web.',
        );
      }
    } catch (err) {
      Alert.alert('Connexion', getErrorMessage(err, 'Identifiants incorrects.'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <ImageBackground 
        source={require('../../../assets/login_bg.jpg')} 
        style={styles.backgroundImage}
      >
        <View style={styles.overlay}>
          <KeyboardAvoidingView 
            behavior={Platform.OS === 'ios' ? 'padding' : 'height'} 
            style={styles.keyboardView}
          >
            <View style={styles.header}>
              <Text style={styles.title}>Connexion</Text>
              <Text style={styles.subtitle}>Accédez à votre espace écologique</Text>
            </View>

            <Card style={styles.card}>
              <Input label="Email" value={email} onChangeText={setEmail} placeholder="vous@email.mg" keyboardType="email-address" />
              <Input label="Mot de passe" value={password} onChangeText={setPassword} secureTextEntry placeholder="••••••••" />
              <Button title="Se connecter" onPress={handleLogin} loading={loading} style={styles.btnLogin} />
              <Button title="Retour" variant="ghost" onPress={() => navigation.goBack()} />
            </Card>
          </KeyboardAvoidingView>
        </View>
      </ImageBackground>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  backgroundImage: { flex: 1, resizeMode: 'cover' },
  overlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.4)', paddingHorizontal: 20 },
  keyboardView: { flex: 1, justifyContent: 'center' },
  header: { marginBottom: 32 },
  title: { fontSize: 36, fontWeight: '800', color: '#fff', marginBottom: 8, textAlign: 'center' },
  subtitle: { fontSize: 16, color: '#f0f9ff', textAlign: 'center' },
  card: { padding: 24, borderRadius: 20 },
  btnLogin: { marginBottom: 12, marginTop: 8 },
});
