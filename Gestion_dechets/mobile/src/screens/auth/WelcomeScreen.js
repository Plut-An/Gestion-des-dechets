import { View, Text, StyleSheet } from 'react-native';
import Screen from '../../components/Screen';
import Button from '../../components/Button';
import Card from '../../components/Card';
import colors from '../../theme/colors';

export default function WelcomeScreen({ navigation }) {
  return (
    <Screen scroll>
      <View style={styles.hero}>
        <Text style={styles.emoji}>🌿</Text>
        <Text style={styles.brand}>ÉcoGestion</Text>
        <Text style={styles.tagline}>
          Ensemble pour une ville plus propre et plus verte.
        </Text>
      </View>
      
      <Card style={styles.cardContainer}>
        <Text style={styles.cardTitle}>Bienvenue !</Text>
        <Text style={styles.cardDesc}>Connectez-vous ou créez un compte pour commencer.</Text>
        
        <Button 
          title="Se connecter" 
          onPress={() => navigation.navigate('Login')} 
          style={styles.mt} 
        />
        <Button
          title="Créer un compte citoyen"
          variant="ghost"
          style={styles.mt}
          onPress={() => navigation.navigate('RegisterCitoyen')}
        />
        <Button
          title="Devenir camioneur"
          variant="ghost"
          style={styles.mt}
          onPress={() => navigation.navigate('RegisterCamioneur')}
        />
      </Card>
    </Screen>
  );
}

const styles = StyleSheet.create({
  hero: { alignItems: 'center', marginBottom: 24, marginTop: 40 },
  emoji: { fontSize: 72, marginBottom: 16 },
  brand: { fontSize: 36, fontWeight: '800', color: colors.primaryDark },
  tagline: { textAlign: 'center', color: colors.textMuted, marginTop: 12, fontSize: 16, lineHeight: 24, paddingHorizontal: 20 },
  cardContainer: { padding: 24, marginTop: 10 },
  cardTitle: { fontSize: 20, fontWeight: '700', color: colors.text, textAlign: 'center', marginBottom: 6 },
  cardDesc: { color: colors.textMuted, textAlign: 'center', marginBottom: 20, fontSize: 14 },
  mt: { marginTop: 14 },
});
