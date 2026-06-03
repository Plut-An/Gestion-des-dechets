import { useCallback, useState } from 'react';
import { Text, FlatList, Alert, StyleSheet, View, ImageBackground } from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import Screen from '../../components/Screen';
import Card from '../../components/Card';
import Button from '../../components/Button';
import { listAssociations, rejoindreAssociation } from '../../api/associations';
import { unwrapList, getErrorMessage } from '../../utils/helpers';
import colors from '../../theme/colors';

export default function AssociationsScreen() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [joiningId, setJoiningId] = useState(null);

  const load = async () => {
    try {
      const data = await listAssociations();
      setItems(unwrapList(data));
    } catch {
      Alert.alert('Erreur', 'Impossible de charger les associations.');
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

  const handleJoin = async (id, nom) => {
    setJoiningId(id);
    try {
      await rejoindreAssociation(id);
      Alert.alert('Demande envoyée', `Votre demande à ${nom} est en attente de validation.`);
    } catch (err) {
      Alert.alert('Erreur', getErrorMessage(err));
    } finally {
      setJoiningId(null);
    }
  };

  return (
    <Screen title="Associations" subtitle="Rejoignez une communauté écologique">
      <FlatList
        data={items}
        keyExtractor={(item) => String(item.id)}
        refreshing={loading}
        onRefresh={load}
        contentContainerStyle={styles.list}
        ListHeaderComponent={
          <View style={styles.bannerContainer}>
            <ImageBackground source={require('../../../assets/community_bg.jpg')} style={styles.bannerImage} imageStyle={styles.bannerImageStyle}>
              <View style={styles.bannerOverlay}>
                <Text style={styles.bannerTitle}>Notre Communauté</Text>
                <Text style={styles.bannerSubtitle}>Ensemble pour agir</Text>
              </View>
            </ImageBackground>
          </View>
        }
        ListEmptyComponent={
          !loading ? <Text style={styles.empty}>Aucune association disponible.</Text> : null
        }
        renderItem={({ item }) => (
          <Card>
            <Text style={styles.nom}>{item.nom}</Text>
            {item.ville ? <Text style={styles.ville}>📍 {item.ville}</Text> : null}
            {item.description ? (
              <Text style={styles.desc} numberOfLines={3}>{item.description}</Text>
            ) : null}
            <Text style={styles.meta}>
              {item.nb_membres ?? 0} membres · {item.nb_camioneurs ?? 0} camioneurs
            </Text>
            <Button
              title="Demander à rejoindre"
              onPress={() => handleJoin(item.id, item.nom)}
              loading={joiningId === item.id}
              style={{ marginTop: 12 }}
            />
          </Card>
        )}
      />
    </Screen>
  );
}

const styles = StyleSheet.create({
  list: { padding: 20, paddingTop: 0 },
  nom: { fontSize: 18, fontWeight: '700', color: colors.text },
  ville: { color: colors.primaryLight, marginTop: 4 },
  desc: { color: colors.textMuted, marginTop: 8, fontSize: 14 },
  meta: { color: colors.textMuted, fontSize: 12, marginTop: 8 },
  empty: { textAlign: 'center', color: colors.textMuted, marginTop: 40 },
  bannerContainer: { marginBottom: 16, borderRadius: 16, elevation: 3, shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 4 },
  bannerImage: { width: '100%', height: 140, justifyContent: 'center' },
  bannerImageStyle: { borderRadius: 16 },
  bannerOverlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.35)', borderRadius: 16, padding: 16, justifyContent: 'center' },
  bannerTitle: { color: 'white', fontSize: 24, fontWeight: '800' },
  bannerSubtitle: { color: 'white', fontSize: 14, fontWeight: '600', marginTop: 4 },
});
