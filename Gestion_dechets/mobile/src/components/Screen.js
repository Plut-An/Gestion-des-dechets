import { SafeAreaView, ScrollView, StyleSheet, View, Text, RefreshControl } from 'react-native';
import colors from '../theme/colors';

export default function Screen({
  title,
  subtitle,
  children,
  scroll,
  refreshing,
  onRefresh,
  headerRight,
}) {
  const content = scroll ? (
    <ScrollView
      contentContainerStyle={styles.scroll}
      refreshControl={
        onRefresh ? (
          <RefreshControl refreshing={!!refreshing} onRefresh={onRefresh} tintColor={colors.primary} />
        ) : undefined
      }
    >
      {children}
    </ScrollView>
  ) : (
    <View style={[styles.body, styles.bodyFlex]}>{children}</View>
  );

  return (
    <SafeAreaView style={styles.safe}>
      {(title || subtitle) && (
        <View style={styles.header}>
          <View style={styles.headerText}>
            {title ? <Text style={styles.title}>{title}</Text> : null}
            {subtitle ? <Text style={styles.subtitle}>{subtitle}</Text> : null}
          </View>
          {headerRight}
        </View>
      )}
      {content}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.background },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingTop: 8,
    paddingBottom: 12,
  },
  headerText: { flex: 1 },
  title: { fontSize: 24, fontWeight: '800', color: colors.text },
  subtitle: { fontSize: 14, color: colors.textMuted, marginTop: 4 },
  scroll: { padding: 20, paddingBottom: 40 },
  body: { padding: 20 },
  bodyFlex: { flex: 1, paddingHorizontal: 0, paddingTop: 0 },
});
