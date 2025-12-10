import javax.crypto.Cipher;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.PBEKeySpec;
import javax.crypto.spec.SecretKeySpec;
import java.security.GeneralSecurityException;
import java.security.Key;
import java.io.IOException;
import java.util.Base64;
import java.io.Closeable;
import java.security.SecureRandom;

public class Main {
    private static final String ALGORITHM = "PBKDF2WithHmacSHA256";
    private static final int KEY_LENGTH_BITS = 256; // AES-256
    private static final int ITERATIONS = 131072; // Number of iterations for PBKDF2, as recommended by NIST guidelines
    private static final int SALT_SIZE_BYTES = 32; // Size of the salt in bytes

    public static void main(String[] args) {
        String message = "Hello, World!";
        byte[] passwordBytes = readPasswordFromUserSecurely();
        SecretKey key = deriveKey(passwordBytes);
        try {
            byte[] encryptedMessage = encrypt(message, key);
            System.out.println("Encrypted Message: " + Base64.getEncoder().encodeToString(encryptedMessage));

            byte[] decryptedMessage = decrypt(Base64.getDecoder().decode(System.console().readLine()), key);
            System.out.println("Decrypted Message: " + new String(decryptedMessage));
        } catch (GeneralSecurityException e) {
            System.err.println("Cryptographic error: " + e.getMessage());
        }
    }

    public static byte[] readPasswordFromUserSecurely() throws IOException {
        java.util.Scanner scanner = new java.util.Scanner(System.in);
        System.out.print("Enter password: ");
        String password = scanner.nextLine();
        return password.getBytes();
    }

    private static SecretKey deriveKey(byte[] password) {
        try (SecureRandom instance = new SecureRandom()) {
            byte[] salt = instance.generateSeed(16);

            try {
                return SecretKeyFactory.getInstance(ALGORITHM).generateSecret(new PBEKeySpec(password, salt, ITERATIONS));
            } catch (GeneralSecurityException e) {
                System.err.println("Failed to derive key: " + e.getMessage());
                throw new RuntimeException(e);
            }
        } catch (IOException | GeneralSecurityException e) {
            System.err.println("Error generating secure random bytes: " + e.getMessage());
            throw new RuntimeException(e);
        }
    }

    private static byte[] encrypt(String message, Key key) throws GeneralSecurityException {
        if (message == null || message.isEmpty()) {
            throw new IllegalArgumentException("Message cannot be null or empty");
        }

        byte[] encryptedMessageBytes = Cipher.getInstance("AES/GCM/NoPadding")
                .doFinal(message.getBytes(), 0, Math.min(256, message.length()), key, createGcmParameterSpec());

        return encryptedMessageBytes;
    }

    private static GCMParameterSpec createGcmParameterSpec() {
        SecureRandom instance = new SecureRandom();
        byte[] iv = instance.generateSeed(12); // Use a SecureRandom instance to generate secure random bytes
        return new GCMParameterSpec(128, iv); // AuthTag size: 128 bits
    }

    private static byte[] decrypt(byte[] encryptedMessage, Key key) throws GeneralSecurityException {
        int colonIndex = -1;
        for (int i = 0; i < encryptedMessage.length - 1; i++) {
            if ((encryptedMessage[i] == ':') && (encryptedMessage[i + 1] != ':')) {
                colonIndex = i;
                break;
            }
        }

        byte[] ivBytes = Arrays.copyOfRange(encryptedMessage, 0, colonIndex);
        byte[] encryptedMessageBytes = Arrays.copyOfRange(encryptedMessage, colonIndex + 1, encryptedMessage.length);

        return Cipher.getInstance("AES/GCM/NoPadding")
                .doFinal(encryptedMessageBytes, 0, Math.min(256, encryptedMessageBytes.length), key, new GCMParameterSpec(128, ivBytes));
    }
}
