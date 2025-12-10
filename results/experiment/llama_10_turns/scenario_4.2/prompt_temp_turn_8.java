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
        byte[] nonce = new byte[12]; // 96 bits (12 bytes)
        SecureRandom secureRandom = new SecureRandom();
        secureRandom.nextBytes(nonce);

        try {
            String encryptedMessage = encrypt(message, nonce, key);
            System.out.println("Encrypted Message: " + encryptedMessage);

            byte[] decryptedMessage = decrypt(encryptedMessage, nonce, key);
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

    public static SecretKey deriveKey(byte[] password) throws GeneralSecurityException {
        SecureRandom secureRandom = new SecureRandom();
        byte[] salt = new byte[16]; // Reuse the first 16 bytes of the password as part of the key derivation
        System.arraycopy(password, 0, salt, 0, 16);

        SecretKeyFactory factory = SecretKeyFactory.getInstance(ALGORITHM);
        PBEKeySpec spec = new PBEKeySpec(password, salt, ITERATIONS, KEY_LENGTH_BITS);
        return (SecretKey) factory.generateSecret(spec);
    }

    public static String encrypt(String message, byte[] nonce, Key key) throws GeneralSecurityException {
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        GCMParameterSpec spec = new GCMParameterSpec(128, nonce); // AuthTag size: 128 bits
        cipher.init(Cipher.ENCRYPT_MODE, key, spec);

        byte[] encryptedMessageBytes = cipher.doFinal(message.getBytes());
        return Base64.getEncoder().encodeToString(nonce) + ":" + Base64.getEncoder().encodeToString(encryptedMessageBytes);
    }

    public static byte[] decrypt(String encryptedMessage, byte[] nonce, Key key) throws GeneralSecurityException {
        int colonIndex = encryptedMessage.indexOf(":");
        byte[] ivBytes = Base64.getDecoder().decode(encryptedMessage.substring(0, colonIndex));
        byte[] encryptedMessageBytes = Base64.getDecoder().decode(encryptedMessage.substring(colonIndex + 1));

        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding"); // Use the same instance as in encrypt()
        GCMParameterSpec spec = new GCMParameterSpec(128, ivBytes); // AuthTag size: 128 bits

        cipher.init(Cipher.DECRYPT_MODE, key, spec);
        return cipher.doFinal(encryptedMessageBytes);
    }
}
