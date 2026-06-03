import { useState } from 'react';
import { View, Text, Image, StyleSheet, Alert, Pressable } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import * as Location from 'expo-location';
import Screen from '../../components/Screen';
import Input from '../../components/Input';
import Button from '../../components/Button';
import { createSignalement } from '../../api/signalements';
import { TYPE_DECHET, getErrorMessage } from '../../utils/helpers';
import colors from '../../theme/colors';

export default function CreateSignalementScreen({ navigation }) {
  const [typeDechet, setTypeDechet] = useState('plastique');
  const [description, setDescription] = useState('');
  const [photo, setPhoto] = useState(null);
  const [coords, setCoords] = useState(null);
  const [loading, setLoading] = useState(false);

  const pickImage = async () => {
    const perm = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!perm.granted) {
      Alert.alert('Permission', 'Accès à la galerie requis.');
      return;
    }
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      quality: 0.7,
    });
    if (!result.canceled) setPhoto(result.assets[0]);
  };

  const getLocation = async () => {
    const { status } = await Location.requestForegroundPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('GPS', 'Autorisez la localisation pour signaler un déchet.');
      return;
    }
    const loc = await Location.getCurrentPositionAsync({});
    setCoords({
      latitude: loc.coords.latitude.toFixed(8),
      longitude: loc.coords.longitude.toFixed(8),
    });
  };

  const submit = async () => {
    if (!coords) {
      Alert.alert('GPS', 'Capturez d\'abord votre position.');
      return;
    }
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('latitude', coords.latitude);
      formData.append('longitude', coords.longitude);
      formData.append('type_dechet', typeDechet);
      formData.append('description', description);
      if (photo) {
        formData.append('photo', {
          uri: photo.uri,
          name: 'signalement.jpg',
          type: 'image/jpeg',
        });
      }
      await createSignalement(formData);
      Alert.alert('Succès', 'Signalement envoyé !', [
        { text: 'OK', onPress: () => navigation.goBack() },
      ]);
    } catch (err) {
      Alert.alert('Erreur', getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Screen title="Nouveau signalement" subtitle="Photo + position GPS" scroll>
      <Text style={styles.label}>Type de déchet</Text>
      <View style={styles.chips}>
        {TYPE_DECHET.map((t) => (
          <Pressable
            key={t.value}
            onPress={() => setTypeDechet(t.value)}
            style={[styles.chip, typeDechet === t.value && styles.chipActive]}
          >
            <Text style={[styles.chipText, typeDechet === t.value && styles.chipTextActive]}>
              {t.label}
            </Text>
          </Pressable>
        ))}
      </View>
      <Input
        label="Description"
        value={description}
        onChangeText={setDescription}
        placeholder="Ex: tas de sacs plastiques..."
        multiline
      />
      <Button title="Prendre / choisir une photo" variant="ghost" onPress={pickImage} />
      {photo ? <Image source={{ uri: photo.uri }} style={styles.preview} /> : null}
      <Button title="Capturer ma position GPS" variant="ghost" onPress={getLocation} />
      {coords ? (
        <Text style={styles.coords}>
          Position : {coords.latitude}, {coords.longitude}
        </Text>
      ) : null}
      <Button title="Envoyer le signalement" onPress={submit} loading={loading} style={{ marginTop: 16 }} />
    </Screen>
  );
}

const styles = StyleSheet.create({
  label: { color: colors.textMuted, marginBottom: 8, fontWeight: '600' },
  chips: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginBottom: 16 },
  chip: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
  },
  chipActive: { backgroundColor: colors.primary, borderColor: colors.primary },
  chipText: { color: colors.textMuted, fontSize: 13 },
  chipTextActive: { color: '#fff', fontWeight: '600' },
  preview: { width: '100%', height: 180, borderRadius: 12, marginVertical: 12 },
  coords: { color: colors.primaryLight, marginVertical: 8, fontSize: 13 },
});
