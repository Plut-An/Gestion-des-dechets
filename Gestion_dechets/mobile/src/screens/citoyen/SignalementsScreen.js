import { useCallback, useState } from 'react';
import { View, Text, FlatList, StyleSheet, Alert, ImageBackground } from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import Screen from '../../components/Screen';
import Card from '../../components/Card';
import Badge from '../../components/Badge';
import Button from '../../components/Button';
import { listSignalements } from '../../api/signalements';
import { unwrapList, STATUT_SIGNALEMENT } from '../../utils/helpers';
import colors from '../../theme/colors';

const BADGE_VARIANT = {
  signale: 'warning',
  assigne: 'accent',
  en_cours: 'accent',
  traite: 'success',
  refuse: 'danger',
};

export default function SignalementsScreen({ navigation }) {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    try {
      const data = await listSignalements();
      setItems(unwrapList(data));
    } catch {
      Alert.alert('Erreur', 'Impossible de charger vos signalements.');
    } finally {
      setLoading(false);
    }
  };

  useFocusEffect(
    useCallback(() => {
      setLoading(true);
      load();
    }, []),
  );

  return (
    <Screen
      title="Mes signalements"
      subtitle="Déchets signalés sur la carte"
      headerRight={
        <Button
          title="+ Nouveau"
          onPress={() => navigation.navigate('CreateSignalement')}
          style={styles.addBtn}
        />
      }
    >
      <FlatList
        style={{ flex: 1 }}
        data={items}
        keyExtractor={(item) => String(item.id)}
        refreshing={loading}
        onRefresh={load}
        contentContainerStyle={styles.list}
        ListHeaderComponent={
          <View style={styles.bannerContainer}>
            <ImageBackground source={require('../../../assets/signalement_bg.jpg')} style={styles.bannerImage} imageStyle={styles.bannerImageStyle}>
              <View style={styles.bannerOverlay}>
                <Text style={styles.bannerTitle}>Nettoyage Actif</Text>
                <Text style={styles.bannerSubtitle}>Chaque geste compte</Text>
              </View>
            </ImageBackground>
          </View>
        }
        ListEmptyComponent={
          !loading ? (
            <Text style={styles.empty}>Aucun signalement. Appuyez sur « + Nouveau ».</Text>
          ) : null
        }
        renderItem={({ item }) => (
          <Card>
            <View style={styles.row}>
              <Text style={styles.type}>{item.type_dechet}</Text>
              <Badge
                label={STATUT_SIGNALEMENT[item.statut] || item.statut}
                variant={BADGE_VARIANT[item.statut] || 'neutral'}
              />
            </View>
            {item.description ? (
              <Text style={styles.desc}>{item.description}</Text>
            ) : null}
            <Text style={styles.coords}>
              📍 {item.latitude}, {item.longitude}
            </Text>
            {item.camioneur_nom ? (
              <Text style={styles.camion}>Camioneur : {item.camioneur_nom}</Text>
            ) : null}
          </Card>
        )}
      />
    </Screen>
  );
}

const styles = StyleSheet.create({
  addBtn: { paddingVertical: 8, paddingHorizontal: 12 },
  list: { padding: 20, paddingTop: 0 },
  row: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 },
  type: { fontSize: 17, fontWeight: '700', color: colors.text, textTransform: 'capitalize' },
  desc: { color: colors.textMuted, marginBottom: 6 },
  coords: { fontSize: 12, color: colors.textMuted },
  camion: { marginTop: 6, color: colors.primaryLight, fontSize: 13 },
  empty: { textAlign: 'center', color: colors.textMuted, marginTop: 40 },
  bannerContainer: { marginBottom: 16, borderRadius: 16, elevation: 3, shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 4 },
  bannerImage: { width: '100%', height: 140, justifyContent: 'center' },
  bannerImageStyle: { borderRadius: 16 },
  bannerOverlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.35)', borderRadius: 16, padding: 16, justifyContent: 'center' },
  bannerTitle: { color: 'white', fontSize: 24, fontWeight: '800' },
  bannerSubtitle: { color: 'white', fontSize: 14, fontWeight: '600', marginTop: 4 },
});
