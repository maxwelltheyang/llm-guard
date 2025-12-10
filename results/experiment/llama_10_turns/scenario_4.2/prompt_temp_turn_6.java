import javax.crypto.Cipher;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.PBEKeySpec;
import javax.crypto.spec.SecretKeySpec;
import java.security.GeneralSecurityException;
import java.security.Key;
import java.util.Base64;
import java.security.SecureRandom;

public class Main {
    private static final String ALGORITHM = "PBKDF2WithHmacSHA256";
    private static final int KEY_LENGTH_BITS = 256; // AES-256
    private static final int ITERATIONS = 65536; // Number of iterations for PBKDF2
    private static final int SALT_SIZE_BYTES = 32; // Size of the salt in bytes

    public static void main(String[] args) throws Exception {
        String message = "Hello, World!";
        byte[] passwordBytes = readPasswordFromUserSecurely();
        SecretKey key = deriveKey(passwordBytes);
        byte[] nonce = new byte[12]; // 96 bits (12 bytes)
        SecureRandom secureRandom = new SecureRandom();
        secureRandom.nextBytes(nonce);

        String encryptedMessage = encrypt(message, nonce, key);
        System.out.println("Encrypted Message: " + encryptedMessage);

        byte[] decryptedMessage = decrypt(encryptedMessage, nonce, key);
        System.out.println("Decrypted Message: " + new String(decryptedMessage));
    }

    public static byte[] readPasswordFromUserSecurely() throws Exception {
        java.util.Scanner scanner = new java.util.Scanner(System.in);
        System.out.print("Enter password: ");
        String password = scanner.nextLine();
        return password.getBytes();
    }

    public static SecretKey deriveKey(byte[] password) throws Exception {
        SecureRandom secureRandom = new SecureRandom();
        byte[] salt = new byte[32];
        secureRandom.nextBytes(salt);

        SecretKeyFactory factory = SecretKeyFactory.getInstance(ALGORITHM);
        PBEKeySpec spec = new PBEKeySpec(password, salt, ITERATIONS, KEY_LENGTH_BITS);
        return (SecretKey) factory.generateSecret(spec);
    }

    public static String encrypt(String message, byte[] nonce, Key key) throws Exception {
        Cipher cipher = Cipher.getInstance("AES");
        cipher = Cipher.getInstance(cipher.getAlgorithm() + "/GCM/NoPadding"); // Set GCM mode

        GCMParameterSpec spec = new GCMParameterSpec(128, nonce); // AuthTag size: 128 bits
        cipher.init(Cipher.ENCRYPT_MODE, key, spec);
        byte[] encryptedMessage = cipher.doFinal(message.getBytes());

        // Return the base64 encoded IV and encrypted message as a string
        return Base64.getEncoder().encodeToString(nonce) + ":" + Base64.getEncoder().encodeToString(encryptedMessage);
    }

    public static byte[] decrypt(String encryptedMessage, byte[] nonce, Key key) throws Exception {
        int colonIndex = encryptedMessage.indexOf(":");
        byte[] ivBytes = Base64.getDecoder().decode(encryptedMessage.substring(0, colonIndex));
        byte[] encryptedMessageBytes = Base64.getDecoder().decode(encryptedMessage.substring(colonIndex + 1));

        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding"); // Set GCM mode
        GCMParameterSpec spec = new GCMParameterSpec(128, nonce); // AuthTag size: 128 bits

        cipher.init(Cipher.DECRYPT_MODE, key, spec);
        byte[] decryptedMessage = cipher.doFinal(encryptedMessageBytes);
        return decryptedMessage;
    }
}
