import javax.crypto.Cipher;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.PBEKeySpec;
import javax.crypto.spec.SecretKeySpec;
import java.security.GeneralSecurityException;
import java.security.Key;
import java.util.Base64;
import java.io.IOException;
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
            String encryptedMessage = encrypt(message, key);
            System.out.println("Encrypted Message: " + encryptedMessage);

            byte[] decryptedMessage = decrypt(encryptedMessage, key);
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

    private static SecretKey deriveKey(byte[] password) throws GeneralSecurityException {
        SecureRandom secureRandom = new SecureRandom();
        byte[] salt = new byte[16]; // Use a SecureRandom instance per operation
        secureRandom.nextBytes(salt);

        try (SecureRandom instance = new SecureRandom()) {
            return SecretKeyFactory.getInstance(ALGORITHM).generateSecret(new PBEKeySpec(password, salt, ITERATIONS));
        }
    }

    private static String encrypt(String message, Key key) throws GeneralSecurityException {
        if (message == null || message.isEmpty()) {
            throw new IllegalArgumentException("Message cannot be null or empty");
        }

        byte[] encryptedMessageBytes = Cipher.getInstance("AES/GCM/NoPadding")
                .doFinal(message.getBytes(), 0, Math.min(256, message.length()), key, createGcmParameterSpec());

        return Base64.getEncoder().encodeToString(encryptedMessageBytes);
    }

    private static GCMParameterSpec createGcmParameterSpec() {
        SecureRandom instance = new SecureRandom();
        byte[] iv = new byte[12];
        instance.nextBytes(iv); // Use a SecureRandom instance per operation
        return new GCMParameterSpec(128, iv); // AuthTag size: 128 bits
    }

    private static byte[] decrypt(String encryptedMessage, Key key) throws GeneralSecurityException {
        int colonIndex = encryptedMessage.indexOf(":");
        if (colonIndex == -1 || colonIndex + 1 >= encryptedMessage.length()) {
            throw new IllegalArgumentException("Invalid input format");
        }

        byte[] ivBytes = Base64.getDecoder().decode(encryptedMessage.substring(0, colonIndex));
        byte[] encryptedMessageBytes = Base64.getDecoder().decode(encryptedMessage.substring(colonIndex + 1));

        return Cipher.getInstance("AES/GCM/NoPadding")
                .doFinal(encryptedMessageBytes, 0, Math.min(256, encryptedMessageBytes.length), key, new GCMParameterSpec(128, ivBytes));
    }
}
