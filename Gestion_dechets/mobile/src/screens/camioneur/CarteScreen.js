import { useCallback, useState, useRef } from 'react';
import { View, Text, FlatList, Alert, StyleSheet, Switch } from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import * as Location from 'expo-location';
import Screen from '../../components/Screen';
import Card from '../../components/Card';
import Badge from '../../components/Badge';
import Button from '../../components/Button';
import { useAuth } from '../../context/AuthContext';
import {
  listSignalementsProches,
  accepterSignalement,
  validerSignalement,
  refuserSignalement,
} from '../../api/signalements';
import { updatePosition } from '../../api/camioneur';
import { getErrorMessage } from '../../utils/helpers';
import colors from '../../theme/colors';

export default function CarteScreen() {
  const { user, refreshProfile } = useAuth();
  const [signalements, setSignalements] = useState([]);
  const [loading, setLoading] = useState(false);
  const [disponible, setDisponible] = useState(
    user?.profil_camioneur?.disponible ?? false,
  );
  const [position, setPosition] = useState(null);
  const intervalRef = useRef(null);

  const profil = user?.profil_camioneur;
  const peutCollecter = profil?.statut_inscription === 'accepte';

  const syncPosition = async () => {
    const { status } = await Location.requestForegroundPermissionsAsync();
    if (status !== 'granted') return null;
    const loc = await Location.getCurrentPositionAsync({});
    const lat = loc.coords.latitude;
    const lng = loc.coords.longitude;
    setPosition({ lat, lng });
    try {
      await updatePosition(String(lat), String(lng), disponible);
    } catch {
      /* ignore */
    }
    return { lat, lng };
  };

  const loadSignalements = async (coords) => {
    if (!coords) return;
    try {
      const data = await listSignalementsProches(coords.lat, coords.lng, 50);
      setSignalements(data.signalements || []);
    } catch (err) {
      Alert.alert('Erreur', getErrorMessage(err));
    }
  };

  const refresh = async () => {
    setLoading(true);
    const coords = await syncPosition();
    if (coords) await loadSignalements(coords);
    setLoading(false);
  };

  useFocusEffect(
    useCallback(() => {
      refresh();
      intervalRef.current = setInterval(refresh, 45000);
      return () => clearInterval(intervalRef.current);
    }, [disponible]),
  );

  const onToggleDispo = async (value) => {
    setDisponible(value);
    if (position) {
      try {
        await updatePosition(String(position.lat), String(position.lng), value);
        await refreshProfile();
      } catch {
        /* ignore */
      }
    }
  };

  const handleAccepter = async (id) => {
    if (!peutCollecter) {
      Alert.alert('Compte', 'Votre compte doit être validé par un administrateur.');
      return;
    }
    try {
      const res = await accepterSignalement(id);
      Alert.alert('Accepté', res.message || 'Bonne collecte !');
      refresh();
    } catch (err) {
      Alert.alert('Erreur', getErrorMessage(err));
    }
  };

  const handleValider = async (id) => {
    try {
      const res = await validerSignalement(id);
      Alert.alert('Validé', res.message || 'Collecte terminée.');
      refresh();
    } catch (err) {
      Alert.alert('Erreur', getErrorMessage(err));
    }
  };

  const handleRefuser = async (id) => {
    try {
      await refuserSignalement(id);
      Alert.alert('Refusé', 'Signalement remis en file d\'attente.');
      refresh();
    } catch (err) {
      Alert.alert('Erreur', getErrorMessage(err));
    }
  };

  return (
    <Screen title="Collectes proches" subtitle="Triés par distance (Haversine)">
      <View style={styles.toolbar}>
        <Text style={styles.dispoLabel}>Disponible</Text>
        <Switch value={disponible} onValueChange={onToggleDispo} trackColor={{ true: colors.primary }} />
        <Button title="Actualiser" variant="ghost" onPress={refresh} loading={loading} style={styles.refreshBtn} />
      </View>
      {!peutCollecter ? (
        <Card>
          <Badge label="Compte en attente de validation admin" variant="warning" />
        </Card>
      ) : null}
      <FlatList
        data={signalements}
        keyExtractor={(item) => String(item.id)}
        contentContainerStyle={styles.list}
        ListEmptyComponent={
          <Text style={styles.empty}>
            {loading ? 'Chargement...' : 'Aucun signalement ouvert à proximité.'}
          </Text>
        }
        renderItem={({ item }) => (
          <Card>
            <View style={styles.row}>
              <Text style={styles.type}>{item.type_dechet}</Text>
              <Badge label={`${item.distance_km} km`} variant="accent" />
            </View>
            {item.description ? <Text style={styles.desc}>{item.description}</Text> : null}
            <Text style={styles.coords}>
              📍 {item.latitude}, {item.longitude}
            </Text>
            {item.statut === 'signale' ? (
              <Button title="Accepter cette collecte" onPress={() => handleAccepter(item.id)} style={{ marginTop: 10 }} />
            ) : (
              <View style={styles.actions}>
                <Button title="Valider" onPress={() => handleValider(item.id)} style={styles.actionBtn} />
                <Button title="Refuser" variant="danger" onPress={() => handleRefuser(item.id)} style={styles.actionBtn} />
              </View>
            )}
          </Card>
        )}
      />
    </Screen>
  );
}

const styles = StyleSheet.create({
  toolbar: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingBottom: 8,
    gap: 8,
  },
  dispoLabel: { color: colors.text, flex: 1 },
  refreshBtn: { paddingVertical: 8, paddingHorizontal: 12 },
  list: { padding: 20, paddingTop: 0 },
  row: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  type: { fontSize: 17, fontWeight: '700', color: colors.text, textTransform: 'capitalize' },
  desc: { color: colors.textMuted, marginTop: 6 },
  coords: { fontSize: 12, color: colors.textMuted, marginTop: 4 },
  actions: { flexDirection: 'row', gap: 8, marginTop: 10 },
  actionBtn: { flex: 1, paddingVertical: 10 },
  empty: { textAlign: 'center', color: colors.textMuted, marginTop: 32 },
});
