import { Text, StyleSheet, ImageBackground, View, TouchableOpacity } from 'react-native';
import Screen from '../../components/Screen';
import Card from '../../components/Card';
import Badge from '../../components/Badge';
import { useAuth } from '../../context/AuthContext';
import { STATUT_INSCRIPTION_LABEL } from '../../utils/helpers';
import colors from '../../theme/colors';
import { Ionicons } from '@expo/vector-icons';

export default function HomeScreen({ navigation }) {
  const { user } = useAuth();
  const profil = user?.profil_citoyen;
  const statut = profil?.statut_inscription || 'en_attente';
  const statutVariant =
    statut === 'accepte' ? 'success' : statut === 'refuse' ? 'danger' : 'warning';

  const headerRight = (
    <TouchableOpacity onPress={() => navigation.navigate('Annonces')} style={styles.headerBtn}>
      <Ionicons name="megaphone-outline" size={24} color={colors.text} />
      <View style={styles.badgeDot} />
    </TouchableOpacity>
  );

  return (
    <Screen
      title={`Bonjour, ${user?.nom?.split(' ')[0] || 'Citoyen'} 👋`}
      subtitle="Votre impact écologique"
      headerRight={headerRight}
      scroll
    >
      <View style={styles.heroContainer}>
        <ImageBackground 
          source={require('../../../assets/home_bg.jpg')} 
          style={styles.heroImage} 
          imageStyle={styles.heroImageRadius}
        >
          <View style={styles.heroOverlay}>
            <Text style={styles.heroTitle}>Éco-points</Text>
            <Text style={styles.heroPoints}>{profil?.solde_eco_points ?? 0}</Text>
            <Badge label={STATUT_INSCRIPTION_LABEL[statut] || statut} variant={statutVariant} />
          </View>
        </ImageBackground>
      </View>

      <Text style={styles.sectionTitle}>Actions rapides</Text>
      <View style={styles.grid}>
        <TouchableOpacity style={styles.gridItem} onPress={() => navigation.navigate('Signalements')}>
          <View style={[styles.iconWrapper, { backgroundColor: '#e0f2fe' }]}>
            <Ionicons name="trash" size={28} color="#0284c7" />
          </View>
          <Text style={styles.gridLabel}>Signaler</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.gridItem} onPress={() => navigation.navigate('Associations')}>
          <View style={[styles.iconWrapper, { backgroundColor: '#dcfce7' }]}>
            <Ionicons name="business" size={28} color="#16a34a" />
          </View>
          <Text style={styles.gridLabel}>Asso</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.gridItem} onPress={() => navigation.navigate('Evenements')}>
          <View style={[styles.iconWrapper, { backgroundColor: '#fef3c7' }]}>
            <Ionicons name="calendar" size={28} color="#d97706" />
          </View>
          <Text style={styles.gridLabel}>Événements</Text>
        </TouchableOpacity>
      </View>

      <Card>
        <Text style={styles.sectionTitle}>Comment gagner des points ?</Text>
        <View style={styles.rowItem}>
          <Ionicons name="checkmark-circle" size={20} color={colors.success} />
          <Text style={styles.hint}>+5 pts par signalement de déchet collecté.</Text>
        </View>
        <View style={styles.rowItem}>
          <Ionicons name="checkmark-circle" size={20} color={colors.success} />
          <Text style={styles.hint}>+10 pts pour participation à un événement.</Text>
        </View>
      </Card>
    </Screen>
  );
}

const styles = StyleSheet.create({
  headerBtn: { padding: 8, position: 'relative' },
  badgeDot: { 
    position: 'absolute', top: 8, right: 8, width: 10, height: 10, 
    borderRadius: 5, backgroundColor: colors.danger, borderWidth: 2, borderColor: colors.background
  },
  heroContainer: { marginBottom: 24, borderRadius: 16, elevation: 4, shadowColor: '#000', shadowOffset: { width: 0, height: 4 }, shadowOpacity: 0.1, shadowRadius: 8 },
  heroImage: { width: '100%', height: 180, justifyContent: 'center' },
  heroImageRadius: { borderRadius: 16 },
  heroOverlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.3)', borderRadius: 16, padding: 20, justifyContent: 'center', alignItems: 'flex-start' },
  heroTitle: { color: 'white', fontSize: 16, fontWeight: '600', marginBottom: 4 },
  heroPoints: { fontSize: 48, fontWeight: '800', color: 'white', marginBottom: 8 },
  sectionTitle: { fontWeight: '800', fontSize: 18, color: colors.text, marginBottom: 16 },
  grid: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 24 },
  gridItem: { flex: 1, alignItems: 'center', backgroundColor: colors.surface, marginHorizontal: 4, paddingVertical: 16, borderRadius: 16, elevation: 2, shadowColor: '#000', shadowOpacity: 0.05, shadowRadius: 4, shadowOffset: { width: 0, height: 2 } },
  iconWrapper: { width: 56, height: 56, borderRadius: 28, justifyContent: 'center', alignItems: 'center', marginBottom: 8 },
  gridLabel: { fontSize: 13, fontWeight: '600', color: colors.textDark },
  rowItem: { flexDirection: 'row', alignItems: 'center', marginBottom: 8, gap: 8 },
  hint: { color: colors.textMuted, fontSize: 14, flex: 1 },
});
