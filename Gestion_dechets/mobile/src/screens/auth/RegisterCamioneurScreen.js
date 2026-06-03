import { useState } from 'react';
import { Alert, StyleSheet, View, ImageBackground, KeyboardAvoidingView, Platform, Text, ScrollView } from 'react-native';
import Input from '../../components/Input';
import Button from '../../components/Button';
import Card from '../../components/Card';
import { useAuth } from '../../context/AuthContext';
import { getErrorMessage } from '../../utils/helpers';
import colors from '../../theme/colors';

export default function RegisterCamioneurScreen({ navigation }) {
  const [form, setForm] = useState({
    nom: '',
    email: '',
    password: '',
    password2: '',
    numero_permis: '',
  });
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();

  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }));

  const handleRegister = async () => {
    if (!form.nom || !form.email || !form.password || !form.numero_permis) {
      Alert.alert('Erreur', 'Tous les champs obligatoires doivent être remplis.');
      return;
    }
    if (form.password !== form.password2) {
      Alert.alert('Erreur', 'Les mots de passe ne correspondent pas.');
      return;
    }
    setLoading(true);
    try {
      await register('camioneur', form);
      Alert.alert(
        'Inscription réussie',
        'Votre compte sera activé après validation par un administrateur.',
      );
    } catch (err) {
      Alert.alert('Inscription', getErrorMessage(err));
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
            <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
              <View style={styles.header}>
                <Text style={styles.title}>Devenir Camionneur</Text>
                <Text style={styles.subtitle}>Collectez les déchets et préservez la nature</Text>
              </View>

              <Card style={styles.card}>
                <Input label="Nom complet" value={form.nom} onChangeText={(v) => set('nom', v)} autoCapitalize="words" />
                <Input label="Email" value={form.email} onChangeText={(v) => set('email', v)} keyboardType="email-address" />
                <Input label="N° permis" value={form.numero_permis} onChangeText={(v) => set('numero_permis', v)} />
                <Input label="Mot de passe" value={form.password} onChangeText={(v) => set('password', v)} secureTextEntry />
                <Input label="Confirmer le mot de passe" value={form.password2} onChangeText={(v) => set('password2', v)} secureTextEntry />
                
                <Button title="S'inscrire" onPress={handleRegister} loading={loading} style={styles.btnRegister} />
                <Button title="Retour" variant="ghost" onPress={() => navigation.goBack()} />
              </Card>
            </ScrollView>
          </KeyboardAvoidingView>
        </View>
      </ImageBackground>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  backgroundImage: { flex: 1, resizeMode: 'cover' },
  overlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.5)', paddingHorizontal: 20 },
  keyboardView: { flex: 1 },
  scrollContent: { flexGrow: 1, justifyContent: 'center', paddingVertical: 40 },
  header: { marginBottom: 32 },
  title: { fontSize: 32, fontWeight: '800', color: '#fff', marginBottom: 8, textAlign: 'center' },
  subtitle: { fontSize: 16, color: '#e0f2fe', textAlign: 'center' },
  card: { padding: 24, borderRadius: 20 },
  btnRegister: { marginBottom: 12, marginTop: 8 },
});
