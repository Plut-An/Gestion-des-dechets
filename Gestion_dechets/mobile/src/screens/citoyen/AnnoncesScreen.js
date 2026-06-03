import { useCallback, useState } from 'react';
import { Text, FlatList, Alert, StyleSheet } from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import Screen from '../../components/Screen';
import Card from '../../components/Card';
import { listAnnonces } from '../../api/evenements';
import { unwrapList } from '../../utils/helpers';
import colors from '../../theme/colors';

export default function AnnoncesScreen() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    try {
      const data = await listAnnonces();
      setItems(unwrapList(data));
    } catch {
      Alert.alert('Erreur', 'Impossible de charger les annonces.');
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
    <Screen title="Annonces" subtitle="Actualités des associations">
      <FlatList
        data={items}
        keyExtractor={(item) => String(item.id)}
        refreshing={loading}
        onRefresh={load}
        contentContainerStyle={styles.list}
        renderItem={({ item }) => (
          <Card>
            <Text style={styles.asso}>{item.association_nom}</Text>
            <Text style={styles.titre}>{item.titre}</Text>
            <Text style={styles.contenu}>{item.contenu}</Text>
            <Text style={styles.date}>
              {new Date(item.date_publication).toLocaleDateString('fr-FR')}
            </Text>
          </Card>
        )}
        ListEmptyComponent={
          !loading ? <Text style={styles.empty}>Aucune annonce pour le moment.</Text> : null
        }
      />
    </Screen>
  );
}

const styles = StyleSheet.create({
  list: { padding: 20, paddingTop: 0 },
  asso: { color: colors.primaryLight, fontSize: 12, fontWeight: '600' },
  titre: { fontSize: 17, fontWeight: '700', color: colors.text, marginTop: 4 },
  contenu: { color: colors.textMuted, marginTop: 8, lineHeight: 20 },
  date: { color: colors.textMuted, fontSize: 11, marginTop: 8 },
  empty: { textAlign: 'center', color: colors.textMuted, marginTop: 40 },
});
