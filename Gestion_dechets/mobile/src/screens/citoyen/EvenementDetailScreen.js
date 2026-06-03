import { useCallback, useState } from 'react';
import { Text, Alert, StyleSheet, View } from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import Screen from '../../components/Screen';
import Card from '../../components/Card';
import Input from '../../components/Input';
import Button from '../../components/Button';
import {
  listEvenements,
  participerEvenement,
  annulerParticipation,
  listCommentaires,
  addCommentaire,
} from '../../api/evenements';
import { unwrapList, getErrorMessage } from '../../utils/helpers';
import colors from '../../theme/colors';

export default function EvenementDetailScreen({ route }) {
  const { id, titre } = route.params;
  const [evenement, setEvenement] = useState(null);
  const [commentaires, setCommentaires] = useState([]);
  const [comment, setComment] = useState('');
  const [loading, setLoading] = useState(false);

  const load = async () => {
    try {
      const evData = await listEvenements();
      const ev = unwrapList(evData).find((e) => e.id === id);
      setEvenement(ev);
      const comData = await listCommentaires(id);
      setCommentaires(unwrapList(comData));
    } catch {
      /* silent */
    }
  };

  useFocusEffect(useCallback(() => { load(); }, [id]));

  const handleParticiper = async () => {
    setLoading(true);
    try {
      const res = await participerEvenement(id);
      Alert.alert('Participation', res.message || 'Inscription enregistrée.');
      load();
    } catch (err) {
      Alert.alert('Erreur', getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const handleAnnuler = async () => {
    try {
      await annulerParticipation(id);
      Alert.alert('Annulé', 'Participation annulée.');
      load();
    } catch (err) {
      Alert.alert('Erreur', getErrorMessage(err));
    }
  };

  const handleComment = async () => {
    if (!comment.trim()) return;
    try {
      await addCommentaire(id, comment.trim());
      setComment('');
      load();
    } catch (err) {
      Alert.alert('Commentaire', getErrorMessage(err));
    }
  };

  return (
    <Screen title={titre || 'Événement'} scroll>
      {evenement ? (
        <Card>
          <Text style={styles.desc}>{evenement.description}</Text>
          <Text style={styles.meta}>📍 {evenement.lieu}</Text>
          <Text style={styles.meta}>
            {new Date(evenement.date_evenement).toLocaleString('fr-FR')}
          </Text>
          {evenement.je_participe ? (
            <Button title="Annuler ma participation" variant="danger" onPress={handleAnnuler} style={{ marginTop: 12 }} />
          ) : (
            <Button title="Participer" onPress={handleParticiper} loading={loading} style={{ marginTop: 12 }} />
          )}
        </Card>
      ) : null}
      <Text style={styles.section}>Commentaires</Text>
      {commentaires.map((c) => (
        <Card key={c.id}>
          <Text style={styles.author}>{c.auteur_nom}</Text>
          <Text style={styles.comText}>{c.contenu}</Text>
        </Card>
      ))}
      <Input label="Ajouter un commentaire" value={comment} onChangeText={setComment} multiline />
      <Button title="Publier" onPress={handleComment} />
    </Screen>
  );
}

const styles = StyleSheet.create({
  desc: { color: colors.text, lineHeight: 22 },
  meta: { color: colors.textMuted, marginTop: 8 },
  section: { fontWeight: '700', color: colors.text, marginVertical: 16, fontSize: 16 },
  author: { fontWeight: '600', color: colors.primaryLight },
  comText: { color: colors.textMuted, marginTop: 4 },
});
