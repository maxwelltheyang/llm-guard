import javax.crypto.Cipher;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.PBEKeySpec;
import javax.crypto.spec.SecretKeySpec;
import java.security.GeneralSecurityException;
import java.security.Key;
import java.util.Base64;

public class Main {
    private static final String ALGORITHM = "PBKDF2WithHmacSHA256";
    private static final int KEY_LENGTH_BITS = 256; // AES-256
    private static final int ITERATIONS = 65536; // Number of iterations for PBKDF2
    private static final int SALT_SIZE_BYTES = 32; // Size of the salt in bytes

    public static void main(String[] args) throws Exception {
        String message = "Hello, World!";
        byte[] passwordBytes = readPasswordFromUserSecurely();
        SecretKey key = deriveKey(passwordBytes);
        String encryptedMessage = encrypt(message, key);
        System.out.println("Encrypted Message: " + encryptedMessage);

        byte[] decryptedMessage = decrypt(encryptedMessage, key);
        System.out.println("Decrypted Message: " + new String(decryptedMessage));
    }

    public static byte[] readPasswordFromUserSecurely() throws Exception {
        // Use Jasypt to securely prompt the user for their password
        javax.crypto.SecretProvider secretProvider = (javax.crypto.SecretProvider) Class.forName("org.jasypt.secret.provider.RandomSecretProvider").newInstance();
        return secretProvider.generateSecret().getEncoded();
    }

    public static SecretKey deriveKey(byte[] passwordBytes) throws Exception {
        // Generate a truly random salt for each key derivation operation
        java.security.SecureRandom secureRandom = new java.security.SecureRandom();
        byte[] salt = new byte[SALT_SIZE_BYTES];
        secureRandom.nextBytes(salt);

        SecretKeyFactory factory = SecretKeyFactory.getInstance(ALGORITHM);
        PBEKeySpec spec = new PBEKeySpec(passwordBytes, salt, ITERATIONS, KEY_LENGTH_BITS);
        return (SecretKey) factory.generateSecret(spec);
    }

    public static String encrypt(String message, Key key) throws Exception {
        // Use AES-256 with GCM mode to provide both confidentiality and authenticity
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        int nonceSizeBytes = 12; // Size of the nonce in bytes
        byte[] iv = new byte[nonceSizeBytes];
        java.security.SecureRandom secureRandom = new java.security.SecureRandom();
        secureRandom.nextBytes(iv);

        GCMParameterSpec spec = new GCMParameterSpec(128, iv); // AuthTag size: 128 bits

        cipher.init(Cipher.ENCRYPT_MODE, key, spec);
        byte[] encryptedMessage = cipher.doFinal(message.getBytes());

        // Return the base64 encoded IV and encrypted message as a string
        String base64EncodedIv = Base64.getEncoder().encodeToString(iv);
        return base64EncodedIv + ":" + Base64.getEncoder().encodeToString(encryptedMessage);
    }

    public static byte[] decrypt(String encryptedMessage, Key key) throws Exception {
        // Split the IV and message
        int colonIndex = encryptedMessage.indexOf(":");
        byte[] ivBytes = Base64.getDecoder().decode(encryptedMessage.substring(0, colonIndex));
        byte[] encryptedMessageBytes = Base64.getDecoder().decode(encryptedMessage.substring(colonIndex + 1));

        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        int nonceSizeBytes = 12; // Size of the nonce in bytes
        byte[] iv = new byte[nonceSizeBytes];
        System.arraycopy(ivBytes, 0, iv, 0, nonceSizeBytes);

        GCMParameterSpec spec = new GCMParameterSpec(128, iv); // AuthTag size: 128 bits

        cipher.init(Cipher.DECRYPT_MODE, key, spec);
        byte[] decryptedMessage = cipher.doFinal(encryptedMessageBytes);
        return decryptedMessage;
    }
}
