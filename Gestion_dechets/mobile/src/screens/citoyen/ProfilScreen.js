import { useState } from 'react';
import { Alert, StyleSheet, Text, View, ImageBackground } from 'react-native';
import Screen from '../../components/Screen';
import Card from '../../components/Card';
import Input from '../../components/Input';
import Button from '../../components/Button';
import { useAuth } from '../../context/AuthContext';
import * as authApi from '../../api/auth';
import { getErrorMessage } from '../../utils/helpers';
import colors from '../../theme/colors';
import { Ionicons } from '@expo/vector-icons';

export default function ProfilScreen() {
  const { user, logout, refreshProfile } = useAuth();
  const [pwd, setPwd] = useState({ ancien: '', nouveau: '', confirmation: '' });
  const [loading, setLoading] = useState(false);

  const changePassword = async () => {
    setLoading(true);
    try {
      await authApi.changePassword({
        ancien_mot_de_passe: pwd.ancien,
        nouveau_mot_de_passe: pwd.nouveau,
        confirmation: pwd.confirmation,
      });
      Alert.alert('Succès', 'Mot de passe modifié.');
      setPwd({ ancien: '', nouveau: '', confirmation: '' });
      await refreshProfile();
    } catch (err) {
      Alert.alert('Erreur', getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    Alert.alert('Déconnexion', 'Voulez-vous vous déconnecter ?', [
      { text: 'Annuler', style: 'cancel' },
      { text: 'Oui', style: 'destructive', onPress: logout },
    ]);
  };

  return (
    <Screen title="Mon profil" scroll>
      <ImageBackground source={require('../../../assets/profil_cover.jpg')} style={styles.coverImage}>
        <View style={styles.coverOverlay}>
          <View style={styles.avatar}>
            <Text style={styles.avatarText}>{user?.nom?.charAt(0)?.toUpperCase()}</Text>
          </View>
          <Text style={styles.profileName}>{user?.nom}</Text>
          <Text style={styles.profileRole}>Citoyen engagé</Text>
        </View>
      </ImageBackground>

      <View style={styles.ecoPointsCard}>
        <Ionicons name="leaf" size={40} color={colors.success} style={styles.leafIcon} />
        <View style={styles.ecoPointsInfo}>
          <Text style={styles.ecoPointsTitle}>Vos Éco-Points</Text>
          <Text style={styles.ecoPointsValue}>{user?.profil_citoyen?.solde_eco_points ?? 0} <Text style={styles.ptsText}>pts</Text></Text>
        </View>
      </View>

      <Card>
        <View style={styles.infoRow}>
          <Ionicons name="mail-outline" size={20} color={colors.textMuted} />
          <View style={styles.infoContent}>
            <Text style={styles.label}>Email</Text>
            <Text style={styles.value}>{user?.email}</Text>
          </View>
        </View>
      </Card>

      <Text style={styles.section}>Sécurité</Text>
      <Card>
        <Input label="Ancien mot de passe" value={pwd.ancien} onChangeText={(v) => setPwd((p) => ({ ...p, ancien: v }))} secureTextEntry />
        <Input label="Nouveau mot de passe" value={pwd.nouveau} onChangeText={(v) => setPwd((p) => ({ ...p, nouveau: v }))} secureTextEntry />
        <Input label="Confirmation" value={pwd.confirmation} onChangeText={(v) => setPwd((p) => ({ ...p, confirmation: v }))} secureTextEntry />
        <Button title="Mettre à jour" onPress={changePassword} loading={loading} style={{ marginTop: 8 }} />
      </Card>

      <Button title="Se déconnecter" variant="danger" onPress={handleLogout} style={{ marginTop: 24 }} />
    </Screen>
  );
}

const styles = StyleSheet.create({
  coverImage: { width: '100%', height: 220, marginBottom: 24, borderRadius: 16, overflow: 'hidden' },
  coverOverlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.4)', justifyContent: 'center', alignItems: 'center', padding: 20 },
  avatar: { width: 80, height: 80, borderRadius: 40, backgroundColor: colors.primary, justifyContent: 'center', alignItems: 'center', marginBottom: 12, borderWidth: 3, borderColor: 'white' },
  avatarText: { fontSize: 32, fontWeight: '800', color: 'white' },
  profileName: { fontSize: 24, fontWeight: '800', color: 'white', marginBottom: 4 },
  profileRole: { fontSize: 14, color: '#e0f2fe', fontWeight: '500' },
  ecoPointsCard: { flexDirection: 'row', backgroundColor: '#ecfdf5', padding: 20, borderRadius: 16, alignItems: 'center', marginBottom: 24, borderWidth: 1, borderColor: '#d1fae5' },
  leafIcon: { marginRight: 16 },
  ecoPointsInfo: { flex: 1 },
  ecoPointsTitle: { fontSize: 14, color: '#065f46', fontWeight: '600', marginBottom: 4, textTransform: 'uppercase' },
  ecoPointsValue: { fontSize: 36, fontWeight: '800', color: '#047857' },
  ptsText: { fontSize: 18, fontWeight: '600' },
  infoRow: { flexDirection: 'row', alignItems: 'center', paddingVertical: 8 },
  infoContent: { marginLeft: 16, flex: 1 },
  label: { color: colors.textMuted, fontSize: 12 },
  value: { color: colors.text, fontSize: 16, fontWeight: '600', marginTop: 2 },
  section: { fontWeight: '800', fontSize: 18, color: colors.text, marginVertical: 16 },
});
