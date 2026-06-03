import { useCallback, useState } from 'react';
import { View, Text, FlatList, Alert, StyleSheet } from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import Screen from '../../components/Screen';
import Card from '../../components/Card';
import Badge from '../../components/Badge';
import { listMesCollectes, validerSignalement, refuserSignalement } from '../../api/signalements';
import { unwrapList, STATUT_SIGNALEMENT, getErrorMessage } from '../../utils/helpers';
import Button from '../../components/Button';
import colors from '../../theme/colors';

const VARIANT = {
  signale: 'warning',
  assigne: 'accent',
  en_cours: 'accent',
  traite: 'success',
  refuse: 'danger',
};

export default function CollectesScreen() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    try {
      const data = await listMesCollectes();
      setItems(unwrapList(data));
    } catch {
      Alert.alert('Erreur', "Impossible de charger l'historique.");
    } finally {
      setLoading(false);
    }
  };

  const handleValider = async (id) => {
    try {
      await validerSignalement(id);
      Alert.alert('Validé', 'Collecte terminée. Le citoyen reçoit +5 éco-points.');
      load();
    } catch (err) {
      Alert.alert('Erreur', getErrorMessage(err));
    }
  };

  const handleRefuser = async (id) => {
    try {
      await refuserSignalement(id);
      Alert.alert('Refusé', 'Signalement remis en file d\'attente.');
      load();
    } catch (err) {
      Alert.alert('Erreur', getErrorMessage(err));
    }
  };

  useFocusEffect(
    useCallback(() => {
      setLoading(true);
      load();
    }, []),
  );

  return (
    <Screen title="Mes collectes" subtitle="Signalements pris en charge">
      <FlatList
        data={items}
        keyExtractor={(item) => String(item.id)}
        refreshing={loading}
        onRefresh={load}
        contentContainerStyle={styles.list}
        renderItem={({ item }) => (
          <Card>
            <Badge label={STATUT_SIGNALEMENT[item.statut] || item.statut} variant={VARIANT[item.statut]} />
            <Text style={styles.type}>{item.type_dechet}</Text>
            <Text style={styles.meta}>Citoyen : {item.citoyen_nom || '—'}</Text>
            <Text style={styles.coords}>📍 {item.latitude}, {item.longitude}</Text>
            {['assigne', 'en_cours'].includes(item.statut) ? (
              <View style={styles.actions}>
                <Button title="Valider" onPress={() => handleValider(item.id)} style={styles.actionBtn} />
                <Button title="Refuser" variant="danger" onPress={() => handleRefuser(item.id)} style={styles.actionBtn} />
              </View>
            ) : null}
          </Card>
        )}
        ListEmptyComponent={
          !loading ? <Text style={styles.empty}>Aucune collecte pour le moment.</Text> : null
        }
      />
    </Screen>
  );
}

const styles = StyleSheet.create({
  list: { padding: 20, paddingTop: 0 },
  type: { fontSize: 17, fontWeight: '700', color: colors.text, marginTop: 8, textTransform: 'capitalize' },
  meta: { color: colors.textMuted, marginTop: 4 },
  coords: { fontSize: 12, color: colors.textMuted, marginTop: 4 },
  empty: { textAlign: 'center', color: colors.textMuted, marginTop: 40 },
  actions: { flexDirection: 'row', gap: 8, marginTop: 12 },
  actionBtn: { flex: 1, paddingVertical: 10 },
});
