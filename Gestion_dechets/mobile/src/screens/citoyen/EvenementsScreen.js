import { useCallback, useState } from 'react';
import { Text, FlatList, Alert, StyleSheet, View, ImageBackground } from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import Screen from '../../components/Screen';
import Card from '../../components/Card';
import Badge from '../../components/Badge';
import { listEvenements } from '../../api/evenements';
import { unwrapList } from '../../utils/helpers';
import colors from '../../theme/colors';

export default function EvenementsScreen({ navigation }) {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    try {
      const data = await listEvenements();
      setItems(unwrapList(data));
    } catch {
      Alert.alert('Erreur', 'Impossible de charger les événements.');
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
    <Screen title="Événements" subtitle="Actions écologiques à venir">
      <FlatList
        data={items}
        keyExtractor={(item) => String(item.id)}
        refreshing={loading}
        onRefresh={load}
        contentContainerStyle={styles.list}
        ListHeaderComponent={
          <View style={styles.bannerContainer}>
            <ImageBackground source={require('../../../assets/event_bg.jpg')} style={styles.bannerImage} imageStyle={styles.bannerImageStyle}>
              <View style={styles.bannerOverlay}>
                <Text style={styles.bannerTitle}>Événements</Text>
                <Text style={styles.bannerSubtitle}>Participez à l'action verte</Text>
              </View>
            </ImageBackground>
          </View>
        }
        renderItem={({ item }) => (
          <Card>
            <Badge label={item.statut} variant="accent" />
            <Text style={styles.titre}>{item.titre}</Text>
            <Text style={styles.asso}>{item.association_nom}</Text>
            <Text style={styles.lieu}>📍 {item.lieu}</Text>
            <Text style={styles.date}>
              {new Date(item.date_evenement).toLocaleString('fr-FR')}
            </Text>
            <Text
              style={styles.link}
              onPress={() => navigation.navigate('EvenementDetail', { id: item.id, titre: item.titre })}
            >
              Voir détails & participer →
            </Text>
          </Card>
        )}
        ListEmptyComponent={
          !loading ? <Text style={styles.empty}>Aucun événement à venir.</Text> : null
        }
      />
    </Screen>
  );
}

const styles = StyleSheet.create({
  list: { padding: 20, paddingTop: 0 },
  titre: { fontSize: 18, fontWeight: '700', color: colors.text, marginTop: 8 },
  asso: { color: colors.primaryLight, marginTop: 4 },
  lieu: { color: colors.textMuted, marginTop: 6 },
  date: { color: colors.textMuted, fontSize: 13, marginTop: 4 },
  link: { color: colors.primary, fontWeight: '600', marginTop: 12 },
  empty: { textAlign: 'center', color: colors.textMuted, marginTop: 40 },
  bannerContainer: { marginBottom: 16, borderRadius: 16, elevation: 3, shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 4 },
  bannerImage: { width: '100%', height: 140, justifyContent: 'center' },
  bannerImageStyle: { borderRadius: 16 },
  bannerOverlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.35)', borderRadius: 16, padding: 16, justifyContent: 'center' },
  bannerTitle: { color: 'white', fontSize: 24, fontWeight: '800' },
  bannerSubtitle: { color: 'white', fontSize: 14, fontWeight: '600', marginTop: 4 },
});
