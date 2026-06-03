import { View, Text, StyleSheet } from 'react-native';
import colors from '../theme/colors';

const VARIANTS = {
  success: { bg: 'rgba(34,197,94,0.2)', color: colors.primaryLight },
  warning: { bg: 'rgba(245,158,11,0.2)', color: colors.warning },
  danger: { bg: 'rgba(239,68,68,0.2)', color: colors.danger },
  neutral: { bg: colors.surfaceLight, color: colors.textMuted },
  accent: { bg: 'rgba(56,189,248,0.2)', color: colors.accent },
};

export default function Badge({ label, variant = 'neutral' }) {
  const v = VARIANTS[variant] || VARIANTS.neutral;
  return (
    <View style={[styles.badge, { backgroundColor: v.bg }]}>
      <Text style={[styles.text, { color: v.color }]}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  badge: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: 8, alignSelf: 'flex-start' },
  text: { fontSize: 12, fontWeight: '600' },
});
