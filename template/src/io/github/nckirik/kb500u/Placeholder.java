package io.github.nckirik.kb500u;

/**
 * The APK contains a real (empty) dex so the package has code, while the
 * manifest receiver is metadata-only. Android reads the receiver metadata when
 * listing keyboard layouts and never instantiates it.
 */
public final class Placeholder {
    private Placeholder() {
    }
}
