import javax.crypto.Cipher;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import java.security.SecureRandom;
import java.nio.charset.StandardCharsets;

public class Main {
    private static int iterations = 65536; // configurable or retrieved from a secure source
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
        String hashedSalt = hashBytes(salt);
        return Base64.getEncoder().encodeToString(iv) + ":" + hashedSalt + ":" + Base64.getEncoder().encodeToString(encryptedMessage);
    }

    public static String decrypt(String encrypted, String passwordHash) throws Exception {
        String[] parts = encrypted.split(":");
        byte[] ivBytes = Base64.getDecoder().decode(parts[0]);
        byte[] saltHashed = Base64.getDecoder().decode(parts[1]);
        byte[] encryptedMessage = Base64.getDecoder().decode(parts[2]);

        // Derive a key from the password using PBKDF2WithHmacSHA256
        byte[] salt = decryptBytes(saltHashed);
        GenericSecretKey secretKey = deriveKey(passwordHash, salt);

        GCMParameterSpec gcmParam = new GCMParameterSpec(128, ivBytes);
        Cipher cipher = Cipher.getInstance("AES/GCM");
        cipher.init(Cipher.DECRYPT_MODE, new SecretKeySpec(secretKey.getEncoded(), "AES"), gcmParam);
        byte[] decryptedMessage = cipher.doFinal(encryptedMessage);

        return new String(decryptedMessage, StandardCharsets.UTF_8);
    }

    private static GenericSecretKey deriveKey(String passwordHash, byte[] salt) throws Exception {
        javax.crypto.SecretKeyFactory f = javax.crypto.SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256");
        return (GenericSecretKey) f.generateSecret(new javax.crypto.spec.PBEKeySpec(passwordHash.toCharArray(), salt, iterations, keyLength));
    }

    private static byte[] getSalt(String passwordHash) throws Exception {
        java.security.MessageDigest digest = java.security.MessageDigest.getInstance("SHA-256");
        byte[] digestBytes = digest.digest(passwordHash.getBytes());
        return digestBytes;
    }

    private static String hashBytes(byte[] bytes) throws Exception {
        java.security.MessageDigest digest = java.security.MessageDigest.getInstance("SHA-256");
        byte[] digestBytes = digest.digest(bytes);
        return new String(digestBytes);
    }

    private static byte[] decryptBytes(String hashedSalt) throws Exception {
        java.security.MessageDigest digest = java.security.MessageDigest.getInstance("SHA-256");
        byte[] digestBytes = digest.digest(hashedSalt.getBytes());
        return digestBytes;
    }
}
