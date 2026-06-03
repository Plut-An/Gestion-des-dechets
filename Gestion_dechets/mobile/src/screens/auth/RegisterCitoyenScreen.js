import { useState } from 'react';
import { Alert, StyleSheet, View, ImageBackground, KeyboardAvoidingView, Platform, Text, ScrollView } from 'react-native';
import Input from '../../components/Input';
import Button from '../../components/Button';
import Card from '../../components/Card';
import { useAuth } from '../../context/AuthContext';
import { getErrorMessage } from '../../utils/helpers';
import colors from '../../theme/colors';

export default function RegisterCitoyenScreen({ navigation }) {
  const [form, setForm] = useState({
    nom: '',
    email: '',
    password: '',
    password2: '',
    adresse: '',
  });
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();

  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }));

  const handleRegister = async () => {
    if (!form.nom || !form.email || !form.password) {
      Alert.alert('Erreur', 'Nom, email et mot de passe sont requis.');
      return;
    }
    if (form.password !== form.password2) {
      Alert.alert('Erreur', 'Les mots de passe ne correspondent pas.');
      return;
    }
    setLoading(true);
    try {
      await register('citoyen', form);
      Alert.alert(
        'Inscription réussie',
        'Votre compte est en attente de validation par un administrateur.',
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
                <Text style={styles.title}>Devenir Citoyen</Text>
                <Text style={styles.subtitle}>Agissez pour la planète dès aujourd'hui</Text>
              </View>

              <Card style={styles.card}>
                <Input label="Nom complet" value={form.nom} onChangeText={(v) => set('nom', v)} autoCapitalize="words" />
                <Input label="Email" value={form.email} onChangeText={(v) => set('email', v)} keyboardType="email-address" />
                <Input label="Adresse" value={form.adresse} onChangeText={(v) => set('adresse', v)} />
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
