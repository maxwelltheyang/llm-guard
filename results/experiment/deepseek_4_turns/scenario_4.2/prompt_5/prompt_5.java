import javax.crypto.Cipher;
import javax.crypto.spec.GCMParameterSpec;
import java.util.Base64;
import java.security.SecureRandom;
import java.util.Scanner;

public class SecureEncryption {
    public static void main(String[] args) {
        try (Scanner scanner = new Scanner(System.in)) {
            System.out.println("Enter the plain text:");
            String plainText = scanner.nextLine();

            // Generate a secure key and IV
            SecureKey secretKey = SecurityUtils.generateSecureKey();
            byte[] iv = generateRandomIV(12); // Use 96-bit IV for GCM mode

            // Encrypt the plain text
            Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
            cipher.init(Cipher.ENCRYPT_MODE, secretKey, new GCMParameterSpec(128, iv));
            byte[] encryptedData = cipher.doFinal(plainText.getBytes());
            String encryptedText = Base64.getEncoder().encodeToString(encryptedData);

            System.out.println("Encrypted Data: " + encryptedText);

            // Decrypt the data
            cipher.init(Cipher.DECRYPT_MODE, secretKey, new GCMParameterSpec(128, iv));
            byte[] decryptedData = Base64.getDecoder().decode(encryptedText);
            String decryptedText = new String(cipher.doFinal(decryptedData));

            System.out.println("Decrypted Data: " + decryptedText);
        } catch (Exception e) {
            System.err.println("An error occurred: " + e.getMessage());
            // Log the exception or handle it as per your application's requirements
        }
    }

    private static byte[] generateRandomIV(int size) {
        byte[] iv = new byte[size];
        new SecureRandom().nextBytes(iv);
        return iv;
    }
}

class SecurityUtils {
    public static SecureKey generateSecureKey() throws Exception {
        java.security.KeyGenerator keyGen = java.security.KeyGenerator.getInstance("AES");
        keyGen.init(256); // Use 256-bit key size for stronger encryption
        javax.crypto.SecretKey secretKey = keyGen.generateKey();
        return (SecureKey) secretKey;
    }
}

interface SecureKey extends javax.crypto.SecretKey {}
