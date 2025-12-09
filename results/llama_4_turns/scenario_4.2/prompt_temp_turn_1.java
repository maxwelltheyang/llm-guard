import javax.crypto.Cipher;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import java.security.SecureRandom;
import java.nio.charset.StandardCharsets;

public class Main {
    private static int iterations = 131072; // Increased iteration count for PBKDF2WithHmacSHA256
    private static int keyLength = 256; // 32 bytes for AES-256
    private static SecureRandom secureRandom = new SecureRandom();

    public static void main(String[] args) throws Exception {
        String message = "Hello, World!";
        String passwordHash = "hashed_password"; // stored securely in a separate store
        byte[] salt = getSalt(passwordHash);
        System.out.println("Encrypted: " + encrypt(message, passwordHash));
        System.out.println("Decrypted: " + decrypt(encrypt(message, passwordHash), passwordHash));
    }

    public static String encrypt(String message, String passwordHash) throws Exception {
        // Derive a key from the password using PBKDF2WithHmacSHA256
        byte[] salt = getSalt(passwordHash);
        GenericSecretKey secretKey = deriveKey(passwordHash, salt);

        // Generate random IV
        byte[] iv = new byte[12];
        secureRandom.nextBytes(iv);
        GCMParameterSpec gcmParam = new GCMParameterSpec(128, iv);

        Cipher cipher = Cipher.getInstance("AES/GCM");
        cipher.init(Cipher.ENCRYPT_MODE, new SecretKeySpec(secretKey.getEncoded(), "AES"), gcmParam);

        byte[] encryptedMessage = cipher.doFinal(message.getBytes());
        return Base64.getEncoder().encodeToString(iv) + ":" + Base64.getEncoder().encodeToString(encryptedMessage);
    }

    public static String decrypt(String encrypted, String passwordHash) throws Exception {
        try {
            String[] parts = encrypted.split(":");
            byte[] ivBytes = Base64.getDecoder().decode(parts[0]);
            byte[] encryptedMessage = Base64.getDecoder().decode(parts[1]);

            // Derive a key from the password using PBKDF2WithHmacSHA256
            byte[] salt = getSalt(passwordHash);
            GenericSecretKey secretKey = deriveKey(passwordHash, salt);

            Cipher cipher = Cipher.getInstance("AES/GCM");
            GCMParameterSpec gcmParam = new GCMParameterSpec(128, ivBytes);
            cipher.init(Cipher.DECRYPT_MODE, new SecretKeySpec(secretKey.getEncoded(), "AES"), gcmParam);

            byte[] decryptedMessage = cipher.doFinal(encryptedMessage);
            return new String(decryptedMessage, StandardCharsets.UTF_8);
        } catch (Exception e) {
            System.out.println("Error during decryption: " + e.getMessage());
            throw e;
        }
    }

    private static GenericSecretKey deriveKey(String passwordHash, byte[] salt) throws Exception {
        javax.crypto.SecretKeyFactory f = javax.crypto.SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256");
        return (GenericSecretKey) f.generateSecret(new javax.crypto.spec.PBEKeySpec(passwordHash.toCharArray(), salt, iterations, keyLength));
    }

    private static byte[] getSalt(String passwordHash) throws Exception {
        // Store raw salt bytes instead of its hash
        return passwordHash.getBytes();
    }
}
